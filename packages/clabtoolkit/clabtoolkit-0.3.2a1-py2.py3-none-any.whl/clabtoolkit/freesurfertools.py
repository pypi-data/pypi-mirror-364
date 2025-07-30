import os
import time
import subprocess
import sys
from glob import glob
from typing import Union
from pathlib import Path
from datetime import datetime
import warnings
import shutil
import json
import uuid
import numpy as np
import nibabel as nib
import pandas as pd

# Importing local modules
from . import misctools as cltmisc
from . import parcellationtools as cltparc
from . import bidstools as cltbids


class AnnotParcellation:
    """
    This class contains methods to work with FreeSurfer annot files

    # Implemented methods:
    # - Correct the parcellation by refilling the vertices from the cortex label file that do not have a label in the annotation file
    # - Convert FreeSurfer annot files to gcs files

    # Methods to be implemented:
    # Grouping regions to create a coarser parcellation
    # Removing regions from the parcellation
    # Correct parcellations by removing small clusters of vertices labeled inside another region

    """

    def __init__(
        self,
        parc_file: str,
        ref_surf: str = None,
        cont_tech: str = "local",
        cont_image: str = None,
    ):
        """
        Initialize the AnnotParcellation object

        Parameters
        ----------
        parc_file     - Required  : Parcellation filename:
        ref_surf      - Optional  : Reference surface. Default is the white surface of the fsaverage subject:
        cont_tech     - Optional  : Container technology. Default is local:
        cont_image    - Optional  : Container image. Default is local:

        """
        booldel = False
        self.filename = parc_file

        # Verify if the file exists
        if not os.path.exists(self.filename):
            raise ValueError("The parcellation file does not exist")

        # Extracting the filename, folder and name
        self.path = os.path.dirname(self.filename)
        self.name = os.path.basename(self.filename)

        # Detecting the hemisphere
        temp_name = self.name.lower()

        # Find in the string annot_name if it is lh. or rh.
        hemi = detect_hemi(self.name)

        self.hemi = hemi

        # If the file is a .gii file, then convert it to a .annot file
        if self.name.endswith(".gii"):

            annot_file = AnnotParcellation.gii2annot(
                self.filename,
                ref_surf=ref_surf,
                annot_file=self.filename.replace(".gii", ".annot"),
                cont_tech=cont_tech,
                cont_image=cont_image,
            )
            booldel = True

        elif self.name.endswith(".annot"):
            annot_file = self.filename

        elif self.name.endswith(".gcs"):
            annot_file = AnnotParcellation.gcs2annot(
                self.filename, annot_file=self.filename.replace(".gcs", ".annot")
            )
            booldel = True

        # Read the annot file using nibabel
        codes, reg_table, reg_names = nib.freesurfer.read_annot(
            annot_file, orig_ids=True
        )

        if booldel:
            os.remove(annot_file)

        # Correcting region names
        reg_names = [name.decode("utf-8") for name in reg_names]

        # Detect the codes in the table that are not in the vertex wise data
        # Find the indexes where the codes are not in the vertex wise data
        tmp_ind = np.where(np.isin(reg_table[:, 4], np.unique(codes)) == False)[0]

        # If there are codes that are not in the vertex wise data, then remove them from the table
        if tmp_ind.size > 0:
            reg_table = np.delete(reg_table, tmp_ind, axis=0)
            reg_names = np.delete(reg_names, tmp_ind).tolist()

        # Storing the codes, colors and names in the object
        self.codes = codes
        self.regtable = reg_table
        self.regnames = reg_names

    def save_annotation(self, out_file: str = None, force: bool = True):
        """
        Save the annotation file. If the file already exists, it will be overwritten.

        Parameters
        ----------
        out_file     - Optional  : Output annotation file:
        force        - Optional  : Force to overwrite the annotation file. Default is True:

        Returns
        -------



        """

        if out_file is None:
            out_file = os.path.join(self.path, self.name)

        # If the directory does not exist then create it
        temp_dir = os.path.dirname(out_file)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        if os.path.exists(out_file) and not force:
            raise ValueError(
                "The annotation file already exists. Set force to True to overwrite it."
            )
        elif os.path.exists(out_file) and force:
            os.remove(out_file)

        # Restructuring the codes to consecutive numbers
        new_codes = np.zeros_like(self.codes) - 1
        for i, code in enumerate(self.regtable[:, 4]):
            new_codes[self.codes == code] = i

        # Save the annotation file
        nib.freesurfer.io.write_annot(out_file, new_codes, self.regtable, self.regnames)

    def fill_parcellation(
        self, label_file: str, surf_file: str, corr_annot: str = None
    ):
        """
        Correct the parcellation by refilling the vertices from the cortex label file that do not have a label in the annotation file.
        @params:
            label_file     - Required  : Label file:
            surf_file      - Required  : Surface file:
            corr_annot     - Optional  : Corrected annotation file. If not provided, it will be saved with the same filename as the original annotation file:

        Returns
        -------
        corr_annot: str
            Corrected annotation file

        """

        # Auxiliary variables for the progress bar
        # LINE_UP = '\033[1A'
        # LINE_CLEAR = '\x1b[2K'

        # Get the vertices from the cortex label file that do not have a label in the annotation file

        # If the surface file does not exist, raise an error, otherwise load the surface
        if os.path.isfile(surf_file):
            vertices, faces = nib.freesurfer.read_geometry(surf_file)
        else:
            raise ValueError(
                "Surface file not found. Annotation, surface and cortex label files are mandatory to correct the parcellation."
            )

        # If the cortex label file does not exist, raise an error, otherwise load the cortex label
        if os.path.isfile(label_file):
            cortex_label = nib.freesurfer.read_label(label_file)
        else:
            raise ValueError(
                "Cortex label file not found. Annotation, surface and cortex label files are mandatory to correct the parcellation."
            )

        vert_lab = self.codes
        # Find the indexes where vert_lab = -1
        tmp_ind = np.where(vert_lab == -1)[0]
        if tmp_ind.size > 0:
            addreg = True
            vert_lab[tmp_ind] = 0
        else:
            addreg = False

        reg_ctable = self.regtable
        reg_names = self.regnames

        ctx_lab = vert_lab[cortex_label].astype(
            int
        )  # Vertices from the cortex label file that have a label in the annotation file

        bool_bound = vert_lab[faces] != 0

        # Boolean variable to check the faces that contain at least two vertices that are different from 0 and at least one vertex that is not 0 (Faces containing the boundary of the parcellation)
        bool_a = np.sum(bool_bound, axis=1) < 3
        bool_b = np.sum(bool_bound, axis=1) > 0
        bool_bound = bool_a & bool_b

        faces_bound = faces[bool_bound, :]
        bound_vert = np.ndarray.flatten(faces_bound)

        vert_lab_bound = vert_lab[bound_vert]

        # Delete from the array bound_vert the vertices that contain the vert_lab_bound different from 0
        bound_vert = np.delete(bound_vert, np.where(vert_lab_bound != 0)[0])
        bound_vert = np.unique(bound_vert)

        # Detect which vertices from bound_vert are in the  cortex_label array
        bound_vert = bound_vert[np.isin(bound_vert, cortex_label)]

        bound_vert_orig = np.zeros(len(bound_vert))
        # Create a while loop to fill the vertices that are in the boundary of the parcellation
        # The loop will end when the array bound_vert is empty or when bound_vert is equal bound_vert_orig

        # Detect if the array bound_vert is equal to bound_vert_orig
        bound = np.array_equal(bound_vert, bound_vert_orig)
        it_count = 0
        while len(bound_vert) > 0:

            if not bound:
                # it_count = it_count + 1
                # cad2print = "Interation number: {} - Vertices to fill: {}".format(
                #     it_count, len(bound_vert))
                # print(cad2print)
                # time.sleep(.5)
                # print(LINE_UP, end=LINE_CLEAR)

                bound_vert_orig = np.copy(bound_vert)
                temp_Tri = np.zeros((len(bound_vert), 100))
                for pos, i in enumerate(bound_vert):
                    # Get the neighbors of the vertex
                    neighbors = np.unique(faces[np.where(faces == i)[0], :])
                    neighbors = np.delete(neighbors, np.where(neighbors == i)[0])
                    temp_Tri[pos, 0 : len(neighbors)] = neighbors
                temp_Tri = temp_Tri.astype(int)
                index_zero = np.where(temp_Tri == 0)
                labels_Tri = vert_lab[temp_Tri]
                labels_Tri[index_zero] = 0

                for pos, i in enumerate(bound_vert):

                    # Get the labels of the neighbors
                    labels = labels_Tri[pos, :]
                    # Get the most frequent label different from 0
                    most_frequent_label = np.bincount(labels[labels != 0]).argmax()

                    # Assign the most frequent label to the vertex
                    vert_lab[i] = most_frequent_label

                ctx_lab = vert_lab[cortex_label].astype(
                    int
                )  # Vertices from the cortex label file that have a label in the annotation file

                bool_bound = vert_lab[faces] != 0

                # Boolean variable to check the faces that contain at least one vertex that is 0 and at least one vertex that is not 0 (Faces containing the boundary of the parcellation)
                bool_a = np.sum(bool_bound, axis=1) < 3
                bool_b = np.sum(bool_bound, axis=1) > 0
                bool_bound = bool_a & bool_b

                faces_bound = faces[bool_bound, :]
                bound_vert = np.ndarray.flatten(faces_bound)

                vert_lab_bound = vert_lab[bound_vert]

                # Delete from the array bound_vert the vertices that contain the vert_lab_bound different from 0
                bound_vert = np.delete(bound_vert, np.where(vert_lab_bound != 0)[0])
                bound_vert = np.unique(bound_vert)

                # Detect which vertices from bound_vert are in the  cortex_label array
                bound_vert = bound_vert[np.isin(bound_vert, cortex_label)]

                bound = np.array_equal(bound_vert, bound_vert_orig)

        if addreg and len(reg_names) != len(np.unique(vert_lab)):
            reg_names = ["unknown"] + reg_names

        # Save the annotation file
        if corr_annot is not None:
            if os.path.isfile(corr_annot):
                os.remove(corr_annot)

            # Create folder if it does not exist
            os.makedirs(os.path.dirname(corr_annot), exist_ok=True)
            self.filename = corr_annot
            self.codes = vert_lab
            self.regtable = reg_ctable
            self.regnames = reg_names

            self.save_annotation(out_file=corr_annot)
        else:
            corr_annot = self.filename

        return corr_annot, vert_lab, reg_ctable, reg_names

    def export_to_tsv(
        self, prefix2add: str = None, reg_offset: int = 1000, tsv_file: str = None
    ):
        """
        Export the table of the parcellation to a tsv file. It will contain the index, the annotation id,
        the parcellation id, the name and the color of the regions.
        If a prefix is provided, it will be added to the names of the regions.
        If a tsv file is provided, it will be saved in the specified path.
        Otherwise it will only return the pandas dataframe.

        Parameters
        ----------
        prefix2add     - Optional  : Prefix to add to the names of the regions:
        reg_offset     - Optional  : Offset to add to the parcellation id. Default is 1000:
        tsv_file       - Optional  : Output tsv file:

        Returns
        -------
        tsv_df: pandas dataframe : Table of the parcellation
        tsv_file: str : Tsv filename

        """

        # Creating the hexadecimal colors for the regions
        parc_hexcolor = cltmisc.multi_rgb2hex(self.regtable[:, 0:3])

        # Creating the region names
        parc_names = self.regnames
        if prefix2add is not None:
            parc_names = cltmisc.correct_names(parc_names, prefix=prefix2add)

        parc_index = np.arange(0, len(parc_names))

        # Selecting the Id in the annotation file
        annot_id = self.regtable[:, 4]

        parc_id = reg_offset + parc_index

        # Creating the dictionary for the tsv files
        tsv_df = pd.DataFrame(
            {
                "index": np.asarray(parc_index),
                "annotid": np.asarray(annot_id),
                "parcid": np.asarray(parc_id),
                "name": parc_names,
                "color": parc_hexcolor,
            }
        )

        # Save the tsv table
        if tsv_file is not None:
            tsv_path = os.path.dirname(tsv_file)

            # Create the directory if it does not exist using the library Path
            tsv_path = Path(tsv_path)

            # If the directory does not exist create the directory and if it fails because it does not have write access send an error
            try:
                tsv_path.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                print("The TemplateFlow directory does not have write access.")
                sys.exit()

            with open(tsv_file, "w+") as tsv_f:
                tsv_f.write(tsv_df.to_csv(sep="\t", index=False))

        return tsv_df, tsv_file
    
    def map_values(self, regional_values: Union[str, pd.DataFrame, np.ndarray], is_dataframe: bool = False) -> Union[np.ndarray, pd.DataFrame]:
        """
        Map the regional values to the vertex wise values using the parcellation codes and region table.
        The regional values can be  a txt file, a pandas dataframe or a numpy array.
        The txt file should contain the regional values in a single column or be a csv file with multiple columns. 
        The number of rows should match the number of regions in the parcellation.
        It will be read as a pandas dataframe with no column names. If the txt file is a csv file, it will be read as a 
        pandas dataframe with column names only if the boolean variable is_dataframe is set to True.

        The pandas dataframe should have the same number of rows as the number of regions in the parcellation and the columns should be the regional values.

        IMPORTANT NOTE:
        The pandas dataframe should cointain columns with numeric values and column names.

        If the regional values are a pandas dataframe, it will be converted to a numpy array.

        The numpy array should have the same number of rows as the number of regions in the parcellation and the columns should be the regional values.
        If the regional values are a numpy array, it will be used as is.
        
        Parameters
        ----------
        regional_values - Required  : Regional values to map to the vertex wise values. It can be a pandas dataframe or a numpy array:

        is_dataframe    - Optional  : If the this variable is set to True, the regional values will be read as a pandas dataframe with column names. Default is False:

        Returns
        -------
        vertex_wise_values: numpy array : Vertex wise values mapped from the regional values

        Raises
        ------
        ValueError
        If the regional values are not a pandas dataframe or a numpy array or if the number of rows does not match the number of regions in the parcellation.

        """
        
        # Check if the regional values are a string (txt file)
        if isinstance(regional_values, str):
            # Check if the file exists
            if not os.path.exists(regional_values):
                raise ValueError("The regional values file does not exist")
            # Read the regional values as a pandas dataframe
            if is_dataframe:
                regional_values = pd.read_csv(
                    regional_values,
                    header=0,
                )
                col_names = regional_values.columns.tolist()
            else:
                regional_values = pd.read_csv(
                    regional_values,
                    header=None,
                )
                col_names = None
            regional_values = regional_values.to_numpy()

        elif isinstance(regional_values, pd.DataFrame):
            # Check if the number of rows matches the number of regions in the parcellation
            if regional_values.shape[0] != len(self.regtable):
                raise ValueError(
                    "The number of rows in the regional values does not match the number of regions in the parcellation"
                )
            else:
                # Check if the columns are numeric
                if not np.issubdtype(regional_values.dtypes[0], np.number):
                    raise ValueError(
                        "The regional values should be numeric"
                    )
                else:
                    # Convert the pandas dataframe to a numpy array
                    col_names = regional_values.columns.tolist()
                    regional_values = regional_values.to_numpy()
                    is_df = True

        elif isinstance(regional_values, np.ndarray):
            col_names = None
            # Check if the number of rows matches the number of regions in the parcellation
            if regional_values.shape[0] != len(self.regtable):
                raise ValueError(
                    "The number of rows in the regional values does not match the number of regions in the parcellation"
                )
        else:
            raise ValueError(
                "The regional values should be a pandas dataframe, a numpy array or a txt file"
            )
                

        vertex_wise_values = create_vertex_values(regional_values, self.codes, self.regtable) 

        if  col_names is not None:
            # If the regional values are a pandas dataframe, then create a dictionary with the column names and the vertex wise values
            vertex_wise_values = pd.DataFrame(
                vertex_wise_values, columns=col_names
            )
        else:
            # If the regional values are a numpy array, then create a numpy array with the vertex wise values
            vertex_wise_values = np.array(vertex_wise_values) 


        return vertex_wise_values


    @staticmethod
    def gii2annot(
        gii_file: str,
        ref_surf: str = None,
        annot_file: str = None,
        cont_tech: str = "local",
        cont_image: str = None,
    ):
        """
        Function to convert FreeSurfer gifti files to annot files using mris_convert

        Parameters
        ----------
        gii_file       - Required  : Gii filename:
        ref_surf       - Optional  : Reference surface. Default is the white surface of the fsaverage subject:
        annot_file     - Optional  : Annot filename:
        cont_tech      - Optional  : Container technology. Default is local:
        cont_image     - Optional  : Container image. Default is local:

        Output
        ------
        gii_file: str : Gii filename

        """

        if not os.path.exists(gii_file):
            raise ValueError("The gii file does not exist")

        if ref_surf is None:

            # Get freesurfer directory
            if "FREESURFER_HOME" in os.environ:
                freesurfer_dir = os.path.join(os.environ["FREESURFER_HOME"], "subjects")
                subj_id = "fsaverage"

                hemi = detect_hemi(gii_file)
                ref_surf = os.path.join(
                    freesurfer_dir, subj_id, "surf", hemi + ".white"
                )
            else:
                raise ValueError(
                    "Impossible to set the reference surface file. Please provide it as an argument"
                )

        else:
            if not os.path.exists(ref_surf):
                raise ValueError("The reference surface file does not exist")

        if annot_file is None:
            annot_file = os.path.join(
                os.path.dirname(gii_file),
                os.path.basename(gii_file).replace(".gii", ".annot"),
            )

        # Generating the bash command
        cmd_bashargs = ["mris_convert", "--annot", gii_file, ref_surf, annot_file]

        cmd_cont = cltmisc.generate_container_command(
            cmd_bashargs, cont_tech, cont_image
        )  # Generating container command
        subprocess.run(
            cmd_cont, stdout=subprocess.PIPE, universal_newlines=True
        )  # Running container command

        return annot_file

    @staticmethod
    def annot2gii(
        annot_file: str,
        ref_surf: str = None,
        gii_file: str = None,
        cont_tech: str = "local",
        cont_image: str = None,
    ):
        """
        Function to convert FreeSurfer annot files to gii files using mris_convert

        Parameters
        ----------
        annot_file     - Required  : Annot filename:
        ref_surf       - Optional  : Reference surface.  Default is the white surface of the fsaverage subject:
        gii_file       - Optional  : Gii filename:
        cont_tech      - Optional  : Container technology. Default is local:
        cont_image     - Optional  : Container image. Default is local:

        Output
        ------
        gii_file: str : Gii filename

        """

        if not os.path.exists(annot_file):
            raise ValueError("The annot file does not exist")

        if ref_surf is None:

            # Get freesurfer directory
            if "FREESURFER_HOME" in os.environ:
                freesurfer_dir = os.path.join(os.environ["FREESURFER_HOME"], "subjects")
                subj_id = "fsaverage"

                hemi = detect_hemi(gii_file)
                ref_surf = os.path.join(
                    freesurfer_dir, subj_id, "surf", hemi + ".white"
                )
            else:
                raise ValueError(
                    "Impossible to set the reference surface file. Please provide it as an argument"
                )

        else:
            if not os.path.exists(ref_surf):
                raise ValueError("The reference surface file does not exist")

        if gii_file is None:
            gii_file = os.path.join(
                os.path.dirname(annot_file),
                os.path.basename(annot_file).replace(".annot", ".gii"),
            )

        if not os.path.exists(annot_file):
            raise ValueError("The annot file does not exist")

        if not os.path.exists(ref_surf):
            raise ValueError("The reference surface file does not exist")

        # Generating the bash command
        cmd_bashargs = ["mris_convert", "--annot", annot_file, ref_surf, gii_file]

        cmd_cont = cltmisc.generate_container_command(
            cmd_bashargs, cont_tech, cont_image
        )  # Generating container command
        subprocess.run(
            cmd_cont, stdout=subprocess.PIPE, universal_newlines=True
        )  # Running container command

    @staticmethod
    def gcs2annot(
        gcs_file: str,
        annot_file: str = None,
        freesurfer_dir: str = None,
        ref_id: str = "fsaverage",
        cont_tech: str = "local",
        cont_image: str = None,
    ):
        """
        Function to convert gcs files to FreeSurfer annot files

        Parameters
        ----------
        gcs_file     - Required  : GCS filename:
        annot_file    - Required  : Annot filename:
        freesurfer_dir - Optional  : FreeSurfer directory. Default is the $SUBJECTS_DIR environment variable:
        ref_id       - Optional  : Reference subject id. Default is fsaverage:
        cont_tech    - Optional  : Container technology. Default is local:
        cont_image   - Optional  : Container image. Default is local:

        Output
        ------
        annot_file: str : Annot filename

        """

        if not os.path.exists(gcs_file):
            raise ValueError("The gcs file does not exist")

        # Set the FreeSurfer directory
        if freesurfer_dir is not None:
            if not os.path.isdir(freesurfer_dir):

                # Create the directory if it does not exist
                freesurfer_dir = Path(freesurfer_dir)
                freesurfer_dir.mkdir(parents=True, exist_ok=True)
                os.environ["SUBJECTS_DIR"] = str(freesurfer_dir)

        else:
            if "SUBJECTS_DIR" not in os.environ:
                raise ValueError(
                    "The FreeSurfer directory must be set in the environment variables or passed as an argument"
                )
            else:
                freesurfer_dir = os.environ["SUBJECTS_DIR"]

                if not os.path.isdir(freesurfer_dir):

                    # Create the directory if it does not exist
                    freesurfer_dir = Path(freesurfer_dir)
                    freesurfer_dir.mkdir(parents=True, exist_ok=True)

        freesurfer_dir = str(freesurfer_dir)

        if not os.path.isdir(freesurfer_dir):

            # Take the default FreeSurfer directory
            if "FREESURFER_HOME" in os.environ:
                freesurfer_dir = os.path.join(os.environ["FREESURFER_HOME"], "subjects")
                ref_id = "fsaverage"
            else:
                raise ValueError(
                    "The FreeSurfer directory must be set in the environment variables or passed as an argument"
                )

        # Set freesurfer directory as subjects directory
        os.environ["SUBJECTS_DIR"] = freesurfer_dir

        hemi_cad = detect_hemi(gcs_file)

        if annot_file is None:
            annot_file = os.path.join(
                os.path.dirname(gcs_file),
                os.path.basename(gcs_file).replace(".gcs", ".annot"),
            )

        ctx_label = os.path.join(
            freesurfer_dir, ref_id, "label", hemi_cad + ".cortex.label"
        )
        aseg_presurf = os.path.join(freesurfer_dir, ref_id, "mri", "aseg.mgz")
        sphere_reg = os.path.join(
            freesurfer_dir, ref_id, "surf", hemi_cad + ".sphere.reg"
        )

        cmd_bashargs = [
            "mris_ca_label",
            "-l",
            ctx_label,
            "-aseg",
            aseg_presurf,
            ref_id,
            hemi_cad,
            sphere_reg,
            gcs_file,
            annot_file,
        ]

        cmd_cont = cltmisc.generate_container_command(
            cmd_bashargs, cont_tech, cont_image
        )  # Generating container command
        subprocess.run(
            cmd_cont, stdout=subprocess.PIPE, universal_newlines=True
        )  # Running container command

        return annot_file

    def annot2tsv(self, tsv_file: str = None):
        """
        Save the annotation file as a tsv file
        @params:
            tsv_file     - Required  : Output tsv file:
        """

        if tsv_file is None:
            tsv_file = os.path.join(self.path, self.name.replace(".annot", ".tsv"))

        # If the directory does not exist then create it
        temp_dir = os.path.dirname(tsv_file)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Save the annotation file
        np.savetxt(tsv_file, self.codes, fmt="%d", delimiter="\t")

        return tsv_file

    def annot2gcs(
        self,
        gcs_file: str = None,
        freesurfer_dir: str = None,
        fssubj_id: str = None,
        hemi: str = None,
        cont_tech: str = "local",
        cont_image: str = None,
    ):
        """
        Convert FreeSurfer annot files to gcs files
        @params:
            annot_file       - Required  : Annot filename:
            gcs_file         - Optional  : GCS filename. If not provided, it will be saved in the same folder as the annot file:
            freesurfer_dir   - Optional  : FreeSurfer directory. Default is the $SUBJECTS_DIR environment variable:
            fssubj_id        - Optional  : FreeSurfer subject id. Default is fsaverage:
            hemi             - Optional  : Hemisphere (lh or rh). If not provided, it will be extracted from the annot filename:
        """

        if gcs_file is None:
            gcs_name = self.name.replace(".annot", ".gcs")

            # Create te gcs folder if it does not exist
            if gcs_folder is None:
                gcs_folder = self.path

            gcs_file = os.path.join(gcs_folder, gcs_name)

        else:
            gcs_name = os.path.basename(gcs_file)
            gcs_folder = os.path.dirname(gcs_file)

        if not os.path.exists(gcs_folder):
            os.makedirs(gcs_folder)

        # Read the colors from annot
        reg_colors = self.regtable[:, 0:3]

        # Create the lookup table for the right hemisphere
        luttable = []
        for roi_pos, roi_name in enumerate(self.regnames):

            luttable.append(
                "{:<4} {:<40} {:>3} {:>3} {:>3} {:>3}".format(
                    roi_pos + 1,
                    roi_name,
                    reg_colors[roi_pos, 0],
                    reg_colors[roi_pos, 1],
                    reg_colors[roi_pos, 2],
                    0,
                )
            )

        # Set the FreeSurfer directory
        if freesurfer_dir is not None:
            if not os.path.isdir(freesurfer_dir):

                # Create the directory if it does not exist
                freesurfer_dir = Path(freesurfer_dir)
                freesurfer_dir.mkdir(parents=True, exist_ok=True)
                os.environ["SUBJECTS_DIR"] = str(freesurfer_dir)

        else:
            if "SUBJECTS_DIR" not in os.environ:
                raise ValueError(
                    "The FreeSurfer directory must be set in the environment variables or passed as an argument"
                )
            else:
                freesurfer_dir = os.environ["SUBJECTS_DIR"]

                if not os.path.isdir(freesurfer_dir):

                    # Create the directory if it does not exist
                    freesurfer_dir = Path(freesurfer_dir)
                    freesurfer_dir.mkdir(parents=True, exist_ok=True)

        # Set the FreeSurfer subject id
        if fssubj_id is None:
            raise ValueError("Please supply a valid subject ID.")

        # If the freesurfer subject directory does not exist, raise an error
        if not os.path.isdir(os.path.join(freesurfer_dir, fssubj_id)):
            raise ValueError(
                "The FreeSurfer subject directory for {} does not exist".format(
                    fssubj_id
                )
            )

        if not os.path.isfile(
            os.path.join(freesurfer_dir, fssubj_id, "surf", "sphere.reg")
        ):
            raise ValueError(
                "The FreeSurfer subject directory for {} does not contain the sphere.reg file".format(
                    fssubj_id
                )
            )

        # Save the lookup table for the left hemisphere
        ctab_file = os.path.join(gcs_folder, self.name + ".ctab")
        with open(ctab_file, "w") as colorLUT_f:
            colorLUT_f.write("\n".join(luttable))

        # Detecting the hemisphere
        if hemi is None:
            hemi = self.hemi
            if hemi is None:
                raise ValueError(
                    "The hemisphere could not be extracted from the annot filename. Please provide it as an argument"
                )

        cmd_bashargs = [
            "mris_ca_train",
            "-n",
            "2",
            "-t",
            ctab_file,
            hemi,
            "sphere.reg",
            self.filename,
            fssubj_id,
            gcs_file,
        ]

        cmd_cont = cltmisc.generate_container_command(
            cmd_bashargs, cont_tech, cont_image
        )  # Generating container command
        subprocess.run(
            cmd_cont, stdout=subprocess.PIPE, universal_newlines=True
        )  # Running container command

        # Delete the ctab file
        os.remove(ctab_file)

        return gcs_name

    def group_into_lobes(
        self,
        grouping: str = "desikan",
        lobes_json: str = None,
        out_annot: str = None,
        ctxprefix: str = None,
        force: bool = False,
    ):
        """
        Function to group into lobes the regions of the parcellation.

        Parameters
        ----------
        grouping       - Required  : Grouping method. Default is desikan:
        lobes_json     - Optional  : Lobes json file: Default is None:
                                        JSON file with the lobes and regions that belong to each lobe.
                                        If not provided, it will use the default lobes json file:
        out_annot      - Optional  : Output annotation file. Default is None:
        ctxprefix      - Optional  : Prefix to add to the names of the regions. Default is None:
        force          - Optional  : Force to overwrite the lobar parcellation. Default is False:

        Output
        ------
        New parcellation object with the regions grouped into lobes

        Examples
        --------
        # Group the regions into lobes using the desikan parcellation
        >>> parc.group_into_lobes(grouping='desikan')

        # Group the regions into lobes using the desikan parcellation and save the new parcellation
        >>> parc.group_into_lobes(grouping='desikan', out_annot='desikan_lobes.annot')

        # Group the regions into lobes using a custom json file. The json file must contain the lobes and regions that belong to each lobe
        in the following format: {"mylobes": {"lobe1": ["region1", "region2"], "lobe2": ["region3", "region4"]}, "colors": {"lobe1": "#FF0000", "lobe2": "#00FF00"}}
        >>> parc.group_into_lobes(grouping='mylobes', lobes_json='lobes.json')

        """

        lobes_dict = load_lobes_json(lobes_json)

        if "lobes" not in lobes_dict.keys():
            lobes_dict = lobes_dict[grouping]

        # Lobes names
        lobe_names = list(lobes_dict["lobes"].keys())

        # Create the new parcellation
        new_codes = np.zeros_like(self.codes)
        orig_codes = np.zeros_like(self.codes)

        reg_codes = self.regtable[:, 4]

        # Create an empty numpy array to store the new table
        rgb = np.array([250, 250, 250])
        vert_val = rgb[0] + rgb[1] * 2**8 + rgb[2] * 2**16
        orig_codes += vert_val

        new_table = np.array([[rgb[0], rgb[1], rgb[2], 0, vert_val]])

        for i, lobe in enumerate(lobe_names):
            lobe_regions = lobes_dict["lobes"][lobe]
            lobe_colors = lobes_dict["colors"][lobe]

            rgb = cltmisc.hex2rgb(lobe_colors)

            # Detect the codes of the regions that belong to the lobe
            reg_indexes = cltmisc.get_indexes_by_substring(self.regnames, lobe_regions)

            if len(reg_indexes) != 0:
                reg_values = reg_codes[reg_indexes]
                vert_val = rgb[0] + rgb[1] * 2**8 + rgb[2] * 2**16
                orig_codes[np.isin(self.codes, reg_values) == True] = vert_val
                new_codes[np.isin(self.codes, reg_values) == True] = i + 1

                # Concatenate the new table
                new_table = np.concatenate(
                    (new_table, np.array([[rgb[0], rgb[1], rgb[2], 0, vert_val]])),
                    axis=0,
                )

        # Remove the first row
        # new_table = new_table[1:, :]
        self.codes = new_codes
        if ctxprefix is not None:
            self.regnames = ["unknown"] + cltmisc.correct_names(
                lobe_names, prefix=ctxprefix
            )
        else:
            self.regnames = ["unknown"] + lobe_names

        self.regtable = new_table
        self.name = ""
        self.path = ""

        # Saving the annot file
        if out_annot is not None:
            self.name = os.path.basename(out_annot)
            self.path = os.path.dirname(out_annot)

            if not os.path.exists(self.path):
                os.makedirs(self.path, exist_ok=True)

            if os.path.exists(out_annot) and not force:
                raise ValueError(
                    "The output annotation file already exists. Use the force option to overwrite it."
                )
            elif os.path.exists(out_annot) and force:
                os.remove(out_annot)

            # Save the annotation file
            self.save_annotation(out_file=out_annot)

        else:
            self.codes = orig_codes


class FreeSurferSubject:
    """
    This class contains methods to work with FreeSurfer subjects.

    """

    def __init__(self, subj_id: str, subjs_dir: str = None):
        """
        This method initializes the FreeSurferSubject object according to the subject id and the subjects directory.
        It reads the FreeSurfer files and stores them in a dictionary.

        Parameters
        ----------

        subj_id: str     - Required  : FreeSurfer subject id:
        subjs_dir: str   - Optional  : FreeSurfer subjects directory. Default is the $SUBJECTS_DIR environment variable:

        Output
        ------
        fs_files: dict : Dictionary with the FreeSurfer files


        """

        if subjs_dir is None:
            self.subjs_dir = os.environ.get("SUBJECTS_DIR")
        else:

            if not os.path.exists(subjs_dir):
                # Create the folder
                os.makedirs(subjs_dir, exist_ok=True)

                print(
                    f"Warning: Directory {subjs_dir} does not exist. It will be created."
                )

            self.subjs_dir = subjs_dir

        subj_dir = os.path.join(self.subjs_dir, subj_id)
        self.subj_id = subj_id

        # Generate a dictionary of the FreeSurfer files
        self.fs_files = {}
        mri_dict = {}
        mri_dict["orig"] = os.path.join(subj_dir, "mri", "orig.mgz")
        mri_dict["brainmask"] = os.path.join(subj_dir, "mri", "brainmask.mgz")
        mri_dict["T1"] = os.path.join(subj_dir, "mri", "T1.mgz")
        mri_dict["talairach"] = os.path.join(
            subj_dir, "mri", "transforms", "talairach.lta"
        )
        vol_parc_dict = {}
        vol_parc_dict["aseg"] = os.path.join(subj_dir, "mri", "aseg.mgz")
        vol_parc_dict["desikan+aseg"] = os.path.join(subj_dir, "mri", "aparc+aseg.mgz")
        vol_parc_dict["destrieux+aseg"] = os.path.join(
            subj_dir, "mri", "aparc.a2009s+aseg.mgz"
        )
        vol_parc_dict["dkt+aseg"] = os.path.join(
            subj_dir, "mri", "aparc.DKTatlas+aseg.mgz"
        )

        vol_parc_dict["ribbon"] = os.path.join(subj_dir, "mri", "ribbon.mgz")
        vol_parc_dict["wm"] = os.path.join(subj_dir, "mri", "wm.mgz")
        vol_parc_dict["wmparc"] = os.path.join(subj_dir, "mri", "wmparc.mgz")

        self.fs_files["mri"] = mri_dict
        self.fs_files["mri"]["parc"] = vol_parc_dict

        # Creating the Surf dictionary
        surf_dict = {}

        lh_s_dict, lh_m_dict, lh_p_dict, lh_t_dict = self.get_hemi_dicts(
            subj_dir=subj_dir, hemi="lh"
        )
        rh_s_dict, rh_m_dict, rh_p_dict, rh_t_dict = self.get_hemi_dicts(
            subj_dir=subj_dir, hemi="rh"
        )

        surf_dict["lh"] = {}
        surf_dict["lh"]["mesh"] = lh_s_dict
        surf_dict["lh"]["map"] = lh_m_dict
        surf_dict["lh"]["parc"] = lh_p_dict

        surf_dict["rh"] = {}
        surf_dict["rh"]["mesh"] = rh_s_dict
        surf_dict["rh"]["map"] = rh_m_dict
        surf_dict["rh"]["parc"] = rh_p_dict

        self.fs_files["surf"] = surf_dict

        # Creating the Stats dictionary
        stats_dict = {}
        global_dict = {}
        global_dict["aseg"] = os.path.join(subj_dir, "stats", "aseg.stats")
        global_dict["wmparc"] = os.path.join(subj_dir, "stats", "wmparc.stats")
        global_dict["brainvol"] = os.path.join(subj_dir, "stats", "brainvol.stats")
        stats_dict["global"] = global_dict
        stats_dict["lh"] = lh_t_dict
        stats_dict["rh"] = rh_t_dict

        self.fs_files["stats"] = stats_dict

    def get_hemi_dicts(self, subj_dir: str, hemi: str):
        """
        This method creates the dictionaries for the hemisphere files.

        Parameters
        ----------
        subj_dir: str     - Required  : FreeSurfer subject ID:

        hemi: str        - Required  : Hemisphere (lh or rh):


        """

        # Surface dictionary
        s_dict = {}
        s_dict["pial"] = os.path.join(subj_dir, "surf", hemi + ".pial")
        s_dict["white"] = os.path.join(subj_dir, "surf", hemi + ".white")
        s_dict["inflated"] = os.path.join(subj_dir, "surf", hemi + ".inflated")
        s_dict["sphere"] = os.path.join(subj_dir, "surf", hemi + ".sphere")
        m_dict = {}
        m_dict["curv"] = os.path.join(subj_dir, "surf", hemi + ".curv")
        m_dict["sulc"] = os.path.join(subj_dir, "surf", hemi + ".sulc")
        m_dict["thickness"] = os.path.join(subj_dir, "surf", hemi + ".thickness")
        m_dict["area"] = os.path.join(subj_dir, "surf", hemi + ".area")
        m_dict["volume"] = os.path.join(subj_dir, "surf", hemi + ".volume")
        m_dict["lgi"] = os.path.join(subj_dir, "surf", hemi + ".pial_lgi")
        p_dict = {}
        p_dict["desikan"] = os.path.join(subj_dir, "label", hemi + ".aparc.annot")
        p_dict["destrieux"] = os.path.join(
            subj_dir, "label", hemi + ".aparc.a2009s.annot"
        )
        p_dict["dkt"] = os.path.join(subj_dir, "label", hemi + ".aparc.DKTatlas.annot")

        # Statistics dictionary
        t_dict = {}
        t_dict["desikan"] = os.path.join(subj_dir, "stats", hemi + ".aparc.stats")
        t_dict["destrieux"] = os.path.join(
            subj_dir, "stats", hemi + ".aparc.a2009s.stats"
        )
        t_dict["dkt"] = os.path.join(subj_dir, "stats", hemi + ".aparc.DKTatlas.stats")
        t_dict["curv"] = os.path.join(subj_dir, "stats", hemi + ".curv.stats")

        return s_dict, m_dict, p_dict, t_dict

    def get_proc_status(self):
        """
        This method checks the processing status

        Parameters
        ----------
        self: object : FreeSurferSubject object

        Returns
        -------
        pstatus: str : Processing status (all, autorecon1, autorecon2, unprocessed)

        """

        # Check if the FreeSurfer subject id exists
        if not os.path.isdir(os.path.join(self.subjs_dir, self.subj_id)):
            pstatus = "unprocessed"
        else:

            # Check if the pial files exist because this file is missing in some FreeSurfer versions
            lh_pial = os.path.join(self.subjs_dir, self.subj_id, "surf", "lh.pial")
            lh_pial_t1 = os.path.join(
                self.subjs_dir, self.subj_id, "surf", "lh.pial.T1"
            )
            rh_pial = os.path.join(self.subjs_dir, self.subj_id, "surf", "rh.pial")
            rh_pial_t1 = os.path.join(
                self.subjs_dir, self.subj_id, "surf", "rh.pial.T1"
            )

            if os.path.isfile(lh_pial_t1) and not os.path.isfile(lh_pial):
                # Copy the lh.pial.T1 to lh.pial
                shutil.copy(lh_pial_t1, lh_pial)

            if os.path.isfile(rh_pial_t1) and not os.path.isfile(rh_pial):
                # Copy the rh.pial.T1 to rh.pial
                shutil.copy(rh_pial_t1, rh_pial)

            # Check the FreeSurfer files
            arecon1_files = [
                self.fs_files["mri"]["T1"],
                self.fs_files["mri"]["brainmask"],
                self.fs_files["mri"]["orig"],
            ]

            arecon2_files = [
                self.fs_files["mri"]["talairach"],
                self.fs_files["mri"]["parc"]["wm"],
                self.fs_files["surf"]["lh"]["mesh"]["pial"],
                self.fs_files["surf"]["rh"]["mesh"]["pial"],
                self.fs_files["surf"]["lh"]["mesh"]["white"],
                self.fs_files["surf"]["rh"]["mesh"]["white"],
                self.fs_files["surf"]["lh"]["mesh"]["inflated"],
                self.fs_files["surf"]["rh"]["mesh"]["inflated"],
                self.fs_files["surf"]["lh"]["map"]["curv"],
                self.fs_files["surf"]["rh"]["map"]["curv"],
                self.fs_files["surf"]["lh"]["map"]["sulc"],
                self.fs_files["surf"]["rh"]["map"]["sulc"],
                self.fs_files["stats"]["lh"]["curv"],
                self.fs_files["stats"]["rh"]["curv"],
            ]

            arecon3_files = [
                self.fs_files["mri"]["parc"]["aseg"],
                self.fs_files["mri"]["parc"]["desikan+aseg"],
                self.fs_files["mri"]["parc"]["destrieux+aseg"],
                self.fs_files["mri"]["parc"]["dkt+aseg"],
                self.fs_files["mri"]["parc"]["wmparc"],
                self.fs_files["mri"]["parc"]["ribbon"],
                self.fs_files["surf"]["lh"]["mesh"]["sphere"],
                self.fs_files["surf"]["rh"]["mesh"]["sphere"],
                self.fs_files["surf"]["lh"]["map"]["thickness"],
                self.fs_files["surf"]["rh"]["map"]["thickness"],
                self.fs_files["surf"]["lh"]["map"]["area"],
                self.fs_files["surf"]["rh"]["map"]["area"],
                self.fs_files["surf"]["lh"]["map"]["volume"],
                self.fs_files["surf"]["rh"]["map"]["volume"],
                self.fs_files["surf"]["lh"]["parc"]["desikan"],
                self.fs_files["surf"]["rh"]["parc"]["desikan"],
                self.fs_files["surf"]["lh"]["parc"]["destrieux"],
                self.fs_files["surf"]["rh"]["parc"]["destrieux"],
                self.fs_files["surf"]["lh"]["parc"]["dkt"],
                self.fs_files["surf"]["rh"]["parc"]["dkt"],
                self.fs_files["stats"]["lh"]["desikan"],
                self.fs_files["stats"]["rh"]["desikan"],
                self.fs_files["stats"]["lh"]["destrieux"],
                self.fs_files["stats"]["rh"]["destrieux"],
                self.fs_files["stats"]["lh"]["dkt"],
                self.fs_files["stats"]["rh"]["dkt"],
            ]

            # Check if the files exist in the FreeSurfer subject directory for auto-recon1
            if all([os.path.exists(f) for f in arecon1_files]):
                arecon1_bool = True
            else:
                arecon1_bool = False

            # Check if the files exist in the FreeSurfer subject directory for auto-recon2
            if all([os.path.exists(f) for f in arecon2_files]):
                arecon2_bool = True
            else:
                arecon2_bool = False

            # Check if the files exist in the FreeSurfer subject directory for auto-recon3
            if all([os.path.exists(f) for f in arecon3_files]):
                arecon3_bool = True
            else:
                arecon3_bool = False

            # Check the processing status
            if arecon3_bool and arecon2_bool and arecon1_bool:
                pstatus = "processed"
            elif arecon2_bool and arecon1_bool and not arecon3_bool:
                pstatus = "autorecon2"
            elif arecon1_bool and not arecon2_bool and not arecon3_bool:
                pstatus = "autorecon1"
            else:
                pstatus = "unprocessed"

        self.pstatus = pstatus

    def launch_freesurfer(
        self,
        t1w_img: str = None,
        proc_stage: Union[str, list] = "all",
        extra_proc: Union[str, list] = None,
        cont_tech: str = "local",
        cont_image: str = None,
        fs_license: str = None,
        force=False,
    ):
        """
        Function to launch recon-all command with different options

        Parameters
        ----------
        t1w_img       - Mandatory : T1w image filename:
        proc_stage    - Optional  : Processing stage. Default is all:
                                    Valid options are: all, autorecon1, autorecon2, autorecon3
        extra_proc    - Optional  : Extra processing stages. Default is None:
                                    Valid options are: lgi, thalamus, brainstem, hippocampus, amygdala, hypothalamus
                                    Some A few freesurfer modules, like subfield/nuclei segmentation tools, require
                                    the matlab runtime package (MCR).
                                    Please go to https://surfer.nmr.mgh.harvard.edu/fswiki/MatlabRuntime
                                    to download the appropriate version of MCR for your system.
        cont_tech    - Optional  : Container technology. Default is local:
        cont_image   - Optional  : Container image. Default is local:
        force        - Optional  : Force the processing. Default is False:

        Output
        ------
        proc_stage: str : Processing stage

        """

        # Set the FreeSurfer directory
        if self.subjs_dir is not None:

            if not os.path.isdir(self.subjs_dir):

                # Create the directory if it does not exist
                self.subjs_dir = Path(self.subjs_dir)
                self.subjs_dir.mkdir(parents=True, exist_ok=True)
                os.environ["SUBJECTS_DIR"] = str(self.subjs_dir)

        else:
            if "SUBJECTS_DIR" not in os.environ:
                raise ValueError(
                    "The FreeSurfer directory must be set in the environment variables or passed as an argument"
                )
            else:
                self.subjs_dir = os.environ["SUBJECTS_DIR"]

                if not os.path.isdir(self.subjs_dir):

                    # Create the directory if it does not exist
                    self.subjs_dir = Path(self.subjs_dir)
                    self.subjs_dir.mkdir(parents=True, exist_ok=True)

        # For containerization
        mount_dirs = []
        if cont_tech == "singularity" or cont_tech == "docker":

            # Detecting the Subjects directorycontainer
            cmd_bashargs = ["echo", "$SUBJECTS_DIR"]
            cmd_cont = cltmisc.generate_container_command(
                cmd_bashargs, cont_tech, cont_image
            )  # Generating container command
            out_cmd = subprocess.run(
                cmd_cont, stdout=subprocess.PIPE, universal_newlines=True
            )
            cont_subjs_dir = out_cmd.stdout.split("\n")[0]
            if cont_tech == "singularity":
                mount_dirs.append("--bind")
            elif cont_tech == "docker":
                mount_dirs.append("-v")
            mount_dirs.append(self.subjs_dir + ":" + cont_subjs_dir)

            # Detecting the Subjects directorycontainer
            cmd_bashargs = ["echo", "$FREESURFER_HOME"]
            cmd_cont = cltmisc.generate_container_command(
                cmd_bashargs, cont_tech, cont_image
            )  # Generating container command
            out_cmd = subprocess.run(
                cmd_cont, stdout=subprocess.PIPE, universal_newlines=True
            )
            cont_license = os.path.join(out_cmd.stdout.split("\n")[0], "license.txt")
            if fs_license is not None:
                if cont_tech == "singularity":
                    mount_dirs.append("--bind")
                elif cont_tech == "docker":
                    mount_dirs.append("-v")
                mount_dirs.append(fs_license + ":" + cont_license)

        # Getting the freesurfer version
        ver_cad = get_version(cont_tech=cont_tech, cont_image=cont_image)
        ver_ent = ver_cad.split(".")
        vert_int = int("".join(ver_ent))

        if not hasattr(self, "pstatus"):
            self.get_proc_status()
        proc_status = self.pstatus

        # Check if the processing stage is valid
        val_stages = ["all", "autorecon1", "autorecon2", "autorecon3"]

        if isinstance(proc_stage, str):
            proc_stage = [proc_stage]

        proc_stage = [stage.lower() for stage in proc_stage]

        for stage in proc_stage:
            if stage not in val_stages:
                raise ValueError(f"Stage {stage} is not valid")

        if "all" in proc_stage:
            proc_stage = ["all"]

        # Check if the extra processing stages are valid
        val_extra_stages = [
            "lgi",
            "thalamus",
            "brainstem",
            "hippocampus",
            "amygdala",
            "hypothalamus",
        ]
        if extra_proc is not None:
            if isinstance(extra_proc, str):
                extra_proc = [extra_proc]

            # Put the extra processing stages in lower case
            extra_proc = [stage.lower() for stage in extra_proc]

            # If hippocampus and amygdala are in the list, remove amygdala from the list
            if "hippocampus" in extra_proc and "amygdala" in extra_proc:
                extra_proc.remove("amygdala")

            for stage in extra_proc:
                if stage not in val_extra_stages:
                    raise ValueError(f"Stage {stage} is not valid")

        if force:

            if t1w_img is None:
                if os.path.isdir(
                    os.path.join(self.subjs_dir, self.subj_id)
                ) and os.path.isfile(self.fs_files["mri"]["orig"]):
                    for st in proc_stage:
                        cmd_bashargs = ["recon-all", "-subjid", self.subj_id, "-" + st]
                        cmd_cont = cltmisc.generate_container_command(
                            cmd_bashargs, cont_tech, cont_image
                        )
                        subprocess.run(
                            cmd_cont,
                            stderr=subprocess.DEVNULL,
                            stdout=subprocess.PIPE,
                            universal_newlines=True,
                        )  # Running container command
            else:
                if os.path.isfile(t1w_img):
                    for st in proc_stage:
                        cmd_bashargs = [
                            "recon-all",
                            "-subjid",
                            self.subj_id,
                            "-i",
                            t1w_img,
                            "-" + st,
                        ]
                        cmd_cont = cltmisc.generate_container_command(
                            cmd_bashargs, cont_tech, cont_image
                        )  # Generating container command
                        subprocess.run(
                            cmd_cont,
                            stderr=subprocess.DEVNULL,
                            stdout=subprocess.PIPE,
                            universal_newlines=True,
                        )  # Running container command
                else:
                    raise ValueError("The T1w image does not exist")
        else:
            if proc_status == "unprocessed":
                if t1w_img is None:
                    if os.path.isdir(
                        os.path.join(self.subjs_dir, self.subj_id)
                    ) and os.path.isfile(self.fs_files["mri"]["orig"]):
                        cmd_bashargs = ["recon-all", "-subjid", self.subj_id, "-all"]
                else:
                    if os.path.isfile(t1w_img):
                        cmd_bashargs = [
                            "recon-all",
                            "-subjid",
                            self.subj_id,
                            "-i",
                            t1w_img,
                            "-all",
                        ]
                    else:
                        raise ValueError("The T1w image does not exist")

                cmd_bashargs = [
                    "recon-all",
                    "-i",
                    t1w_img,
                    "-subjid",
                    self.subj_id,
                    "-all",
                ]
                cmd_cont = cltmisc.generate_container_command(
                    cmd_bashargs, cont_tech, cont_image
                )  # Generating container command
                subprocess.run(
                    cmd_cont,
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    universal_newlines=True,
                )  # Running container command
            elif proc_status == "autorecon1":
                cmd_bashargs = ["recon-all", "-subjid", self.subj_id, "-autorecon2"]
                cmd_cont = cltmisc.generate_container_command(
                    cmd_bashargs, cont_tech, cont_image
                )  # Generating container command
                subprocess.run(
                    cmd_cont,
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    universal_newlines=True,
                )  # Running container command

                cmd_bashargs = ["recon-all", "-subjid", self.subj_id, "-autorecon3"]
                cmd_cont = cltmisc.generate_container_command(
                    cmd_bashargs, cont_tech, cont_image
                )  # Generating container command
                subprocess.run(
                    cmd_cont,
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    universal_newlines=True,
                )  # Running container command

            elif proc_status == "autorecon2":
                cmd_bashargs = ["recon-all", "-subjid", self.subj_id, "-autorecon3"]
                cmd_cont = cltmisc.generate_container_command(
                    cmd_bashargs, cont_tech, cont_image
                )
                subprocess.run(
                    cmd_cont,
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    universal_newlines=True,
                )  # Running container command

        self.get_proc_status()
        proc_status = self.pstatus

        # Processing extra stages
        if extra_proc is not None:
            if isinstance(extra_proc, str):
                extra_proc = [extra_proc]

            cmd_list = []
            for stage in extra_proc:
                if stage in val_extra_stages:
                    if stage == "lgi":  # Compute the local gyrification index

                        if (
                            not os.path.isfile(
                                self.fs_files["surf"]["lh"]["map"]["lgi"]
                            )
                            and not os.path.isfile(
                                self.fs_files["surf"]["rh"]["map"]["lgi"]
                            )
                        ) or force == True:
                            cmd_bashargs = [
                                "recon-all",
                                "-subjid",
                                self.subj_id,
                                "-lgi",
                            ]
                            cmd_list.append(cmd_bashargs)

                    elif (
                        stage == "thalamus"
                    ):  # Segment the thalamic nuclei using the thalamic nuclei segmentation tool

                        th_files = glob(
                            os.path.join(
                                self.subjs_dir, self.subj_id, "mri", "ThalamicNuclei.*"
                            )
                        )

                        if len(th_files) != 3 or force == True:
                            if vert_int < 730:
                                cmd_bashargs = [
                                    "segmentThalamicNuclei.sh",
                                    self.subj_id,
                                    self.subjs_dir,
                                ]
                            else:
                                cmd_bashargs = [
                                    "segment_subregions",
                                    "thalamus",
                                    "--cross",
                                    self.subj_id,
                                ]

                            cmd_list.append(cmd_bashargs)

                    elif stage == "brainstem":  # Segment the brainstem structures

                        bs_files = glob(
                            os.path.join(
                                self.subjs_dir, self.subj_id, "mri", "brainstemS*"
                            )
                        )

                        if len(bs_files) != 3 or force == True:
                            os.system("WRITE_POSTERIORS=1")
                            if vert_int < 730:
                                cmd_bashargs = [
                                    "segmentBS.sh",
                                    self.subj_id,
                                    self.subjs_dir,
                                ]
                            else:
                                cmd_bashargs = [
                                    "segment_subregions",
                                    "brainstem",
                                    "--cross",
                                    self.subj_id,
                                ]

                            cmd_list.append(cmd_bashargs)

                    elif (
                        stage == "hippocampus" or stage == "amygdala"
                    ):  # Segment the hippocampal subfields

                        ha_files = glob(
                            os.path.join(
                                self.subjs_dir,
                                self.subj_id,
                                "mri",
                                "*hippoAmygLabels.*",
                            )
                        )

                        if len(ha_files) != 16 or force == True:
                            if (
                                vert_int < 730
                            ):  # Use the FreeSurfer script for versions below 7.2.0
                                cmd_bashargs = [
                                    "segmentHA_T1.sh",
                                    self.subj_id,
                                    self.subjs_dir,
                                ]
                            else:
                                cmd_bashargs = [
                                    "segment_subregions",
                                    "hippo-amygdala",
                                    "--cross",
                                    self.subj_id,
                                ]

                            cmd_list.append(cmd_bashargs)

                    elif stage == "hypothalamus":  # Segment the hypothalamic subunits

                        hy_files = glob(
                            os.path.join(
                                self.subjs_dir,
                                self.subj_id,
                                "mri",
                                "hypothalamic_subunits*",
                            )
                        )
                        os.system("WRITE_POSTERIORS=1")
                        if len(hy_files) != 3 or force == True:
                            cmd_bashargs = [
                                "mri_segment_hypothalamic_subunits",
                                "--s",
                                self.subj_id,
                                "--sd",
                                self.subjs_dir,
                                "--write_posteriors",
                            ]
                            cmd_list.append(cmd_bashargs)

            if len(cmd_list) > 0:

                for cmd_bashargs in cmd_list:
                    cmd_cont = cltmisc.generate_container_command(
                        cmd_bashargs, cont_tech, cont_image
                    )
                    cmd_cont = cmd_cont[:2] + mount_dirs + cmd_cont[2:]

                    subprocess.run(
                        cmd_cont,
                        stderr=subprocess.DEVNULL,
                        stdout=subprocess.PIPE,
                        universal_newlines=True,
                    )  # Running container command

        return proc_status

    def create_stats_table(
        self,
        lobes_grouping: str = "desikan",
        add_bids_entities: bool = False,
        output_file: str = None,
    ) -> pd.DataFrame:
        """
        Generates a comprehensive FreeSurfer statistics table by combining
        surface-based morphometric metrics and volumetric measurements.

        This function retrieves cortical and volumetric measurements from
        FreeSurfer outputs and organizes them into a structured DataFrame.

        Parameters
        ----------
        lobes_grouping : str, optional
            Parcellation grouping method for lobar segmentation. Default is "desikan".
            Valid options:
            - "desikan" : Standard Desikan-Killiany atlas.
            - "desikan+cingulate" : Includes an additional lobe including cingulate regions.

        output_file : str, optional
            Path to save the final DataFrame as a CSV file. If None (default),
            the table is not saved.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing FreeSurfer statistics, including:
            - Surface-based morphometric measurements (left & right hemispheres).
            - Volumetric measurements.
        """

        import morphometrytools as morpho

        # Compute morphometric statistics
        lh_surf_df = self.surface_hemi_morpho(hemi="lh", lobes_grouping=lobes_grouping)
        rh_surf_df = self.surface_hemi_morpho(hemi="rh", lobes_grouping=lobes_grouping)
        vol_df = self.volume_morpho()

        # Adding the volumes extracted by FreeSurfer and stored at aseg.stats
        stats_df, _ = morpho.parse_freesurfer_stats_fromaseg(
            self.fs_files["stats"]["global"]["aseg"], add_bids_entities=False
        )
        stats_df.insert(4, "Atlas", "")

        # Parsing global metrics from aseg.mgz
        global_df, _ = morpho.parse_freesurfer_global_fromaseg(
            self.fs_files["stats"]["global"]["aseg"], add_bids_entities=False
        )
        global_df.insert(4, "Atlas", "")

        # Combine all data into a single DataFrame
        stats_table = pd.concat(
            [global_df, stats_df, vol_df, lh_surf_df, rh_surf_df], axis=0
        )

        # Adding the entities related to BIDs
        if add_bids_entities:
            ent_list = morpho.entities4table(selected_entities=self.subj_id)

            df_add = cltbids.entities_to_table(
                filepath=self.subj_id, entities_to_extract=ent_list
            )

            stats_table = cltmisc.expand_and_concatenate(df_add, stats_table)
        else:
            # Expand a first dataframe and concatenate with the second dataframe
            stats_table.insert(0, "Participant", self.subj_id)

        # Adding the table as an attribute
        self.stats_table = stats_table

        # Save the DataFrame to a file if an output path is specified
        if output_file:
            stats_table.to_csv(output_file, index=False)
            print(f"Statistics table saved to: {output_file}")

        return stats_table

    def volume_morpho(
        self,
        parcellations: list = ["desikan+aseg", "destrieux+aseg", "dkt+aseg"],
        lobes_grouping: str = "desikan",
    ) -> pd.DataFrame:
        """
        Computes the volume of brain regions based on the specified parcellations.

        This function extracts volumetric measurements from the provided FreeSurfer
        parcellations and returns a DataFrame containing volume values.

        Parameters
        ----------
        parcellations : list, optional
            List of parcellation names for which to compute volume.
            Default is ["desikan+aseg", "destrieux+aseg", "dkt+aseg"].

        lobes_grouping : str, optional
            Parcellation grouping method for lobar segmentation. Default is "desikan".
            Valid options:
            - "desikan" : Standard Desikan-Killiany atlas.
            - "desikan+cingulate" : Includes additional cingulate regions.

        Returns
        -------
        pd.DataFrame
            DataFrame containing volume values per region, with columns:
            - "atlas_id" : Name of the parcellation atlas.
            - "source" : Measurement source (set as "volume").
            - Other columns contain computed volume values for each region.
        """

        from . import parcellationtools as parc

        # Initialize an empty DataFrame for results
        df_vol = pd.DataFrame()

        # Iterate over each specified parcellation
        for volparc in parcellations:
            parc_file = self.fs_files["mri"]["parc"].get(volparc, None)
            if not parc_file or not os.path.isfile(parc_file):
                continue  # Skip missing parcellations

            # Load parcellation and compute volume table
            vol_parc = parc.Parcellation(parc_file=parc_file)
            vol_parc.load_colortable()
            vol_parc.compute_volume_table()
            df, _ = vol_parc.volumetable

            # Add identifying columns
            df.insert(4, "Atlas", volparc)

            # Concatenate results
            df_vol = pd.concat([df_vol, df], axis=0)

        nrows = df_vol.shape[0]

        return df_vol

    def surface_hemi_morpho(
        self, hemi: str = "lh", lobes_grouping: str = "desikan", verbose: bool = False
    ) -> pd.DataFrame:
        """
        Computes morphometric metrics for a given hemisphere using cortical surface maps
        and parcellations from FreeSurfer.

        This function extracts various morphometric properties such as mean thickness,
        surface area, and Euler characteristic from the provided cortical surfaces,
        maps, and parcellations.

        Parameters
        ----------
        hemi : str, optional
            Hemisphere to process ("lh" for left hemisphere, "rh" for right hemisphere).
            Default is "lh".

        lobes_grouping : str, optional
            Parcellation grouping method for lobar segmentation. Default is "desikan".
            Valid options:
            - "desikan" : Standard Desikan-Killiany atlas.
            - "desikan+cingulate" : Includes additional cingulate regions.

        Returns
        -------
        pd.DataFrame
            DataFrame containing computed morphometric values, including:
            - Mean cortical thickness per region.
            - Surface area measurements (pial and white surfaces).
            - Euler characteristic values.
            Each row corresponds to a different region or measurement source.
        """

        from . import morphometrytools as morpho

        # Retrieve relevant FreeSurfer files
        parc_files_dict = self.fs_files["surf"][hemi]["parc"]
        metric_files_dict = self.fs_files["surf"][hemi]["map"]
        pial_surf = self.fs_files["surf"][hemi]["mesh"]["pial"]
        white_surf = self.fs_files["surf"][hemi]["mesh"]["white"]

        # Initialize DataFrame for results
        df_hemi = pd.DataFrame()

        # Process lobar parcellation
        desikan_parc = parc_files_dict.get("desikan", None)
        include_lobes = os.path.isfile(desikan_parc) if desikan_parc else False
        if include_lobes:
            # Print  Step 0: Grouping into lobes
            if verbose:
                print(" ")
                print("Step 0: Grouping into lobes")
                start_time = time.time()

            lobar_obj = AnnotParcellation(parc_file=desikan_parc)
            lobar_obj.group_into_lobes(grouping=lobes_grouping)

            # Compute the elapsed time and print it
            if verbose:
                elapsed_time = time.time() - start_time
                print(f"Elapsed time: {elapsed_time:.2f} seconds")

        # Iterate over parcellations
        if verbose:
            print(" ")
            print(
                f"Step 1: Computing morphometric metrics for the {hemi.upper()} hemisphere"
            )
        n_parc = len(parc_files_dict)
        cont_parc = 0
        for parc_name, parc_file in parc_files_dict.items():
            cont_parc += 1
            if not os.path.isfile(parc_file):
                continue  # Skip missing parcellations

            # Extract base name without extensions
            parc_base_name = ".".join(os.path.basename(parc_file).split(".")[1:-1])
            if parc_base_name == "aparc":
                parc_base_name = "desikan"
            elif parc_base_name == "aparc.a2009s":
                parc_base_name = "destrieux"
            elif parc_base_name == "aparc.DKTatlas":
                parc_base_name = "dkt"

            if verbose:
                print(" ")
                print(
                    f"    - Step 1.1: Surface-based metrics (Parcellation: {parc_base_name} [{cont_parc}/{n_parc}])"
                )

            df_metric = pd.DataFrame()

            # Compute mean thickness per region
            n_metrics = len(metric_files_dict)
            cont_metric = 0
            for metric_name, metric_file in metric_files_dict.items():
                if not os.path.isfile(metric_file):
                    continue

                cont_metric += 1
                if verbose:
                    print(
                        f"        - Metric: {metric_name} [{cont_metric}/{n_metrics+1}]"
                    )
                    start_time = time.time()

                # Compute lobar and regional metrics
                df_lobes, _, _ = morpho.compute_reg_val_fromannot(
                    metric_file,
                    lobar_obj,
                    hemi,
                    metric=metric_name,
                    add_bids_entities=False,
                )
                df_lobes.insert(4, "Atlas", f"lobes_{lobes_grouping}")

                df_region, _, _ = morpho.compute_reg_val_fromannot(
                    metric_file,
                    parc_file,
                    hemi,
                    metric=metric_name,
                    include_global=False,
                    add_bids_entities=False,
                )
                df_region.insert(4, "Atlas", parc_base_name)

                # Concatenate results
                df_metric = pd.concat([df_metric, df_lobes, df_region], axis=0)
                if verbose:
                    elapsed_time = time.time() - start_time
                    print(f"        Elapsed time: {elapsed_time:.2f} seconds")

            # Compute surface area and Euler characteristic for both pial and white surfaces
            df_parc = pd.DataFrame()
            df_e = pd.DataFrame()
            cont_metric += 1
            cont_euler = cont_metric + 1
            for surface, source_label in zip(
                [pial_surf, white_surf], ["pial", "white"]
            ):
                start_time = time.time()
                df_area_region, _ = morpho.compute_reg_area_fromsurf(
                    surface,
                    parc_file,
                    hemi,
                    include_global=False,
                    add_bids_entities=False,
                    surf_type=source_label,
                )

                df_area_region.insert(4, "Atlas", parc_base_name)

                df_area_lobes, _ = morpho.compute_reg_area_fromsurf(
                    surface,
                    lobar_obj,
                    hemi,
                    surf_type=source_label,
                    add_bids_entities=False,
                )
                df_area_lobes.insert(4, "Atlas", f"lobes_{lobes_grouping}")

                if verbose:
                    print(
                        f"        - Metric: {surface.capitalize()} Surface Area [{cont_metric}/{n_metrics+1}]"
                    )
                    elapsed_time = time.time() - start_time
                    print(f"        Elapsed time: {elapsed_time:.2f} seconds")

                # Compute Euler characteristic
                start_time = time.time()
                df_euler, _ = morpho.compute_euler_fromsurf(
                    surface, hemi, surf_type=source_label, add_bids_entities=False
                )

                if verbose:
                    print(
                        f"        - Metric: Euler Characteristic for {surface.capitalize()} Surface [{cont_euler}/{n_metrics+1}]"
                    )
                    elapsed_time = time.time() - start_time
                    print(f"        Elapsed time: {elapsed_time:.2f} seconds")

                df_euler.insert(4, "Atlas", "")

                # Concatenate all the results
                df_parc = pd.concat(
                    [df_parc, df_area_lobes, df_area_region, df_euler], axis=0
                )

            if verbose:
                print(" ")
                print(
                    f"    - Step 1.2: Metrics from Stats files (Parcellation: {parc_base_name})"
                )
                start_time = time.time()

            # Read the stats file
            stat_file = self.fs_files["stats"][hemi][parc_name]

            df_stats_cortex, _ = morpho.parse_freesurfer_cortex_stats(
                stat_file, add_bids_entities=False
            )
            if verbose:
                elapsed_time = time.time() - start_time
                print(f"        Elapsed time: {elapsed_time:.2f} seconds")

            df_stats_cortex.insert(4, "Atlas", parc_base_name)

            # Merge morphometric and area metrics
            if not df_metric.empty:
                df_parc = pd.concat([df_parc, df_metric], axis=0)

            if not df_parc.empty:
                df_hemi = pd.concat([df_hemi, df_parc, df_stats_cortex], axis=0)

        return df_hemi

    @staticmethod
    def set_freesurfer_directory(fs_dir: str = None):
        """
        Function to set up the FreeSurfer directory

        Parameters
        ----------
        fs_dir       - Optional  : FreeSurfer directory. Default is None:
                                If not provided, it will be extracted from the
                                $SUBJECTS_DIR environment variable. If it does not exist,
                                it will be created.

        Output
        ------
        fs_dir: str : FreeSurfer directory
        """

        # Set the FreeSurfer directory
        if fs_dir is None:

            if "SUBJECTS_DIR" not in os.environ:
                raise ValueError(
                    "The FreeSurfer directory must be set in the environment variables or passed as an argument"
                )
            else:
                fs_dir = os.environ["SUBJECTS_DIR"]

        # Create the directory if it does not exist
        fs_dir = Path(fs_dir)
        fs_dir.mkdir(parents=True, exist_ok=True)
        os.environ["SUBJECTS_DIR"] = str(fs_dir)

    def annot2ind(
        self,
        ref_id: str,
        hemi: str,
        fs_annot: str,
        ind_annot: str,
        cont_tech: str = "local",
        cont_image: str = None,
        force=False,
        verbose=False,
    ):
        """
        Map ANNOT parcellation files to individual space.

        Parameters:
        ----------
        ref_id : str
            FreeSurfer ID for the reference subject

        hemi : str
            Hemisphere id ("lh" or "rh")

        fs_annot : str
            FreeSurfer GCS parcellation file

        ind_annot : str
            Annotation file in individual space

        cont_tech : str
            Container technology ("singularity", "docker", "local")

        cont_image: str
            Container image to use

        force : bool
            Force the processing

        verbose : bool
            Verbose mode. Default is False.

        """

        if not os.path.isfile(fs_annot) and not os.path.isfile(
            os.path.join(
                self.subjs_dir, ref_id, "label", hemi + "." + fs_annot + ".annot"
            )
        ):
            raise FileNotFoundError(
                f"Files {fs_annot} or {os.path.join(self.subjs_dir, ref_id, 'label', hemi + '.' + fs_annot + '.annot')} do not exist"
            )

        if fs_annot.endswith(".gii"):
            tmp_annot = fs_annot.replace(".gii", ".annot")
            tmp_refsurf = os.path.join(
                self.subjs_dir, ref_id, "surf", hemi + ".inflated"
            )

            AnnotParcellation.gii2annot(
                gii_file=fs_annot,
                ref_surf=tmp_refsurf,
                annot_file=tmp_annot,
                cont_tech=cont_tech,
                cont_image=cont_image,
            )
            fs_annot = tmp_annot

        if not os.path.isfile(ind_annot) or force:

            FreeSurferSubject.set_freesurfer_directory(self.subjs_dir)

            # Create the folder if it does not exist
            temp_dir = os.path.dirname(ind_annot)
            temp_dir = Path(temp_dir)
            temp_dir.mkdir(parents=True, exist_ok=True)

            if cont_tech != "local":
                cmd_bashargs = ["echo", "$SUBJECTS_DIR"]
                cmd_cont = cltmisc.generate_container_command(
                    cmd_bashargs, cont_tech, cont_image
                )  # Generating container command
                out_cmd = subprocess.run(
                    cmd_cont, stdout=subprocess.PIPE, universal_newlines=True
                )
                subjs_dir_cont = out_cmd.stdout.split("\n")[0]
                dir_cad = self.subjs_dir + ":" + subjs_dir_cont

            # Moving the Annot to individual space
            cmd_bashargs = [
                "mri_surf2surf",
                "--srcsubject",
                ref_id,
                "--trgsubject",
                self.subj_id,
                "--hemi",
                hemi,
                "--sval-annot",
                fs_annot,
                "--tval",
                ind_annot,
            ]
            cmd_cont = cltmisc.generate_container_command(
                cmd_bashargs, cont_tech, cont_image
            )  # Generating container command

            # Bind the FreeSurfer subjects directory
            if cont_tech == "singularity":
                cmd_cont.insert(2, "--bind")
                cmd_cont.insert(3, dir_cad)
            elif cont_tech == "docker":
                cmd_cont.insert(2, "-v")
                cmd_cont.insert(3, dir_cad)

            subprocess.run(
                cmd_cont,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )  # Running container command

            # Correcting the parcellation file in order to refill the parcellation with the correct labels
            cort_parc = AnnotParcellation(parc_file=ind_annot)
            label_file = os.path.join(
                self.subjs_dir, self.subj_id, "label", hemi + ".cortex.label"
            )
            surf_file = os.path.join(
                self.subjs_dir, self.subj_id, "surf", hemi + ".inflated"
            )
            cort_parc.fill_parcellation(
                corr_annot=ind_annot, label_file=label_file, surf_file=surf_file
            )

        elif os.path.isfile(ind_annot) and not force:
            # Print a message
            if verbose:
                print(
                    f"File {ind_annot} already exists. Use force=True to overwrite it"
                )

        return ind_annot

    def gcs2ind(
        self,
        fs_gcs: str,
        ind_annot: str,
        hemi: str,
        cont_tech: str = "local",
        cont_image: str = None,
        force=False,
        verbose=False,
    ):
        """
        Map GCS parcellation files to individual space.

        Parameters:
        ----------
        fs_gcs : str
            FreeSurfer GCS parcellation file

        ind_annot : str
            Individual space annotation file

        hemi : str
            Hemisphere id ("lh" or "rh")

        cont_tech : str
            Container technology ("singularity", "docker", "local")

        cont_image: str
            Container image to use

        force : bool
            Force the processing

        verbose : bool
            Verbose mode. Default is False.

        """

        if not os.path.isfile(ind_annot) or force:

            FreeSurferSubject.set_freesurfer_directory(self.subjs_dir)

            # Create the folder if it does not exist
            temp_dir = os.path.dirname(ind_annot)
            temp_dir = Path(temp_dir)
            temp_dir.mkdir(parents=True, exist_ok=True)

            if cont_tech != "local":
                cmd_bashargs = ["echo", "$SUBJECTS_DIR"]
                cmd_cont = cltmisc.generate_container_command(
                    cmd_bashargs, cont_tech, cont_image
                )  # Generating container command
                out_cmd = subprocess.run(
                    cmd_cont, stdout=subprocess.PIPE, universal_newlines=True
                )
                subjs_dir_cont = out_cmd.stdout.split("\n")[0]
                dir_cad = self.subjs_dir + ":" + subjs_dir_cont

            # Moving the GCS to individual space
            cort_file = os.path.join(
                self.subjs_dir, self.subj_id, "label", hemi + ".cortex.label"
            )
            sph_file = os.path.join(
                self.subjs_dir, self.subj_id, "surf", hemi + ".sphere.reg"
            )

            cmd_bashargs = [
                "mris_ca_label",
                "-l",
                cort_file,
                self.subj_id,
                hemi,
                sph_file,
                fs_gcs,
                ind_annot,
            ]

            cmd_cont = cltmisc.generate_container_command(
                cmd_bashargs, cont_tech, cont_image
            )  # Generating container command

            # Bind the FreeSurfer subjects directory
            if cont_tech == "singularity":
                cmd_cont.insert(2, "--bind")
                cmd_cont.insert(3, dir_cad)
            elif cont_tech == "docker":
                cmd_cont.insert(2, "-v")
                cmd_cont.insert(3, dir_cad)

            subprocess.run(
                cmd_cont,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )  # Running container command

            # Correcting the parcellation file in order to refill the parcellation with the correct labels
            cort_parc = AnnotParcellation(parc_file=ind_annot)
            label_file = os.path.join(
                self.subjs_dir, self.subj_id, "label", hemi + ".cortex.label"
            )
            surf_file = os.path.join(
                self.subjs_dir, self.subj_id, "surf", hemi + ".inflated"
            )
            cort_parc.fill_parcellation(
                corr_annot=ind_annot, label_file=label_file, surf_file=surf_file
            )

        elif os.path.isfile(ind_annot) and not force:
            # Print a message
            if verbose:
                print(
                    f"File {ind_annot} already exists. Use force=True to overwrite it"
                )

        return ind_annot

    def surf2vol(
        self,
        atlas: str,
        out_vol: str,
        gm_grow: Union[int, str] = "0",
        color_table: Union[list, str] = None,
        bool_native: bool = False,
        bool_mixwm: bool = False,
        cont_tech: str = "local",
        cont_image: str = None,
        force: bool = False,
        verbose: bool = False,
    ):
        """
        Create volumetric parcellation from annot files.

        Parameters:
        ----------
        atlas : str
            Atlas ID

        out_vol : str
            Output volumetric parcellation file

        gm_grow : list or str
            Amount of milimiters to grow the GM labels

        color_table : list or str
            Save a color table in tsv or lookup table. The options are 'tsv' or 'lut'.
            A list with both formats can be also provided (e.g. ['tsv', 'lut'] ).

        bool_native : bool
            If True, the parcellation will be in native space. The parcellation in native space
            will be saved in Nifti-1 format.

        bool_mixwm : bool
            Mix the cortical WM growing with the cortical GM. This will be used to extend the cortical
            GM inside the WM.

        cont_tech : str
            Container technology ("singularity", "docker", "local")

        cont_image: str
            Container image to use

        force : bool
            Force the processing.

        verbose : bool
            Verbose mode. Default is False.

        """

        FreeSurferSubject.set_freesurfer_directory(self.subjs_dir)

        if cont_tech != "local":
            cmd_bashargs = ["echo", "$SUBJECTS_DIR"]
            cmd_cont = cltmisc.generate_container_command(
                cmd_bashargs, cont_tech, cont_image
            )  # Generating container command
            out_cmd = subprocess.run(
                cmd_cont, stdout=subprocess.PIPE, universal_newlines=True
            )
            subjs_dir_cont = out_cmd.stdout.split("\n")[0]
            dir_cad = self.subjs_dir + ":" + subjs_dir_cont

        if isinstance(gm_grow, int):
            gm_grow = str(gm_grow)

        if color_table is not None:
            if isinstance(color_table, str):
                color_table = [color_table]

            if not isinstance(color_table, list):
                raise ValueError(
                    "color_table must be a list or a string with its elements equal to tsv or lut"
                )

            # Check if the elements of the list are tsv or lut. If the elements are not tsv or lut delete them
            # Lower all the elements in the list
            color_table = cltmisc.filter_by_substring(
                color_table, ["tsv", "lut"], bool_case=False
            )

            # If the list is empty set its value to None
            if len(color_table) == 0:
                color_table = ["lut"]

            if cont_tech != "local":
                cmd_bashargs = ["echo", "$FREESURFER_HOME"]
                cmd_cont = cltmisc.generate_container_command(
                    cmd_bashargs, cont_tech, cont_image
                )  # Generating container command
                out_cmd = subprocess.run(
                    cmd_cont, stdout=subprocess.PIPE, universal_newlines=True
                )
                fslut_file_cont = os.path.join(
                    out_cmd.stdout.split("\n")[0], "FreeSurferColorLUT.txt"
                )
                tmp_name = str(uuid.uuid4())
                cmd_bashargs = ["cp", "replace_cad", "/tmp/" + tmp_name]
                cmd_cont = cltmisc.generate_container_command(
                    cmd_bashargs, cont_tech, cont_image
                )

                # Replace the element of the list equal to replace_cad by the path of the lut file
                cmd_cont = [w.replace("replace_cad", fslut_file_cont) for w in cmd_cont]
                subprocess.run(
                    cmd_cont, stdout=subprocess.PIPE, universal_newlines=True
                )
                fslut_file = os.path.join("/tmp", tmp_name)

                lut_dict = cltparc.Parcellation.read_luttable(in_file=fslut_file)

                # Remove the temporary file
                os.remove(fslut_file)

            else:

                fslut_file = os.path.join(
                    os.environ.get("FREESURFER_HOME"), "FreeSurferColorLUT.txt"
                )
                lut_dict = cltparc.Parcellation.read_luttable(in_file=fslut_file)

            fs_codes = lut_dict["index"]
            fs_names = lut_dict["name"]
            fs_colors = lut_dict["color"]

        # Create the folder if it does not exist
        temp_dir = os.path.dirname(out_vol)
        temp_dir = Path(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)

        if not os.path.isfile(out_vol) or force:

            if gm_grow == "0":

                cmd_bashargs = [
                    "mri_aparc2aseg",
                    "--s",
                    self.subj_id,
                    "--annot",
                    atlas,
                    "--hypo-as-wm",
                    "--new-ribbon",
                    "--o",
                    out_vol,
                ]

            elif gm_grow == "wm":
                cmd_bashargs = [
                    "mri_aparc2aseg",
                    "--s",
                    self.subj_id,
                    "--annot",
                    atlas,
                    "--labelwm",
                    "--hypo-as-wm",
                    "--new-ribbon",
                    "--o",
                    out_vol,
                ]

            else:
                # Creating the volumetric parcellation using the annot files
                cmd_bashargs = [
                    "mri_aparc2aseg",
                    "--s",
                    self.subj_id,
                    "--annot",
                    atlas,
                    "--wmparc-dmax",
                    gm_grow,
                    "--labelwm",
                    "--hypo-as-wm",
                    "--new-ribbon",
                    "--o",
                    out_vol,
                ]

            cmd_cont = cltmisc.generate_container_command(
                cmd_bashargs, cont_tech, cont_image
            )  # Generating container command

            # Bind the FreeSurfer subjects directory
            if cont_tech == "singularity":
                cmd_cont.insert(2, "--bind")
                cmd_cont.insert(3, dir_cad)
            elif cont_tech == "docker":
                cmd_cont.insert(2, "-v")
                cmd_cont.insert(3, dir_cad)

            subprocess.run(
                cmd_cont,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )  # Running container command

            if bool_native:

                # Moving the resulting parcellation from conform space to native
                self.conform2native(
                    mgz_conform=out_vol, nii_native=out_vol, force=force
                )

            if bool_mixwm:

                # Substracting 2000 to the WM labels in order to mix them with the GM labels
                parc = cltparc.Parcellation(parc_file=out_vol)
                parc_vol = parc.data

                # Detect the values in parc_vol that are bigger than 3000 and smaller than 5000
                # and substrac 2000 from them
                mask = np.logical_and(parc_vol >= 3000, parc_vol < 5000)
                parc_vol[mask] = parc_vol[mask] - 2000
                parc.data = parc_vol
                parc.adjust_values
                parc.save_parcellation(out_file=out_vol)

            if color_table is not None:
                temp_iparc = nib.load(out_vol)

                # unique the values
                unique_vals = np.unique(temp_iparc.get_fdata())

                # Select only the values different from 0 that are lower than 1000 or higher than 5000
                unique_vals = unique_vals[unique_vals != 0]
                unique_vals = unique_vals[(unique_vals < 1000) | (unique_vals > 5000)]

                # print them as integer numbers
                unique_vals = unique_vals.astype(int)

                fs_colortable = os.path.join(
                    os.environ.get("FREESURFER_HOME"), "FreeSurferColorLUT.txt"
                )
                lut_dict = cltparc.Parcellation.read_luttable(in_file=fs_colortable)
                fs_codes = lut_dict["index"]
                fs_names = lut_dict["name"]
                fs_colors = lut_dict["color"]

                values, idx = cltmisc.ismember_from_list(fs_codes, unique_vals.tolist())

                # select the fs_names and fs_colors in the indexes idx
                selected_fs_code = [fs_codes[i] for i in idx]
                selected_fs_name = [fs_names[i] for i in idx]
                selected_fs_color = [fs_colors[i] for i in idx]

                selected_fs_color = cltmisc.multi_rgb2hex(selected_fs_color)

                lh_ctx_parc = os.path.join(
                    self.subjs_dir, self.subj_id, "label", "lh." + atlas + ".annot"
                )
                rh_ctx_parc = os.path.join(
                    self.subjs_dir, self.subj_id, "label", "rh." + atlas + ".annot"
                )

                lh_obj = AnnotParcellation(parc_file=lh_ctx_parc)
                rh_obj = AnnotParcellation(parc_file=rh_ctx_parc)

                df_lh, out_tsv = lh_obj.export_to_tsv(
                    prefix2add="ctx-lh-", reg_offset=1000
                )
                df_rh, out_tsv = rh_obj.export_to_tsv(
                    prefix2add="ctx-rh-", reg_offset=2000
                )

                # Convert the column name of the dataframe to a list
                lh_ctx_code = df_lh["parcid"].tolist()
                rh_ctx_code = df_rh["parcid"].tolist()

                # Convert the column name of the dataframe to a list
                lh_ctx_name = df_lh["name"].tolist()
                rh_ctx_name = df_rh["name"].tolist()

                # Convert the column color of the dataframe to a list
                lh_ctx_color = df_lh["color"].tolist()
                rh_ctx_color = df_rh["color"].tolist()

                if gm_grow == "0" or bool_mixwm:
                    all_codes = selected_fs_code + lh_ctx_code + rh_ctx_code
                    all_names = selected_fs_name + lh_ctx_name + rh_ctx_name
                    all_colors = selected_fs_color + lh_ctx_color + rh_ctx_color

                else:

                    lh_wm_name = cltmisc.correct_names(
                        lh_ctx_name, replace=["ctx-lh-", "wm-lh-"]
                    )
                    # Add 2000 to each element of the list lh_ctx_code to create the WM code
                    lh_wm_code = [x + 2000 for x in lh_ctx_code]

                    rh_wm_name = cltmisc.correct_names(
                        rh_ctx_name, replace=["ctx-rh-", "wm-rh-"]
                    )
                    # Add 2000 to each element of the list lh_ctx_code to create the WM code
                    rh_wm_code = [x + 2000 for x in rh_ctx_code]

                    # Invert the colors lh_wm_color and rh_wm_color
                    ilh_wm_color = cltmisc.invert_colors(lh_ctx_color)
                    irh_wm_color = cltmisc.invert_colors(rh_ctx_color)

                    all_codes = (
                        selected_fs_code
                        + lh_ctx_code
                        + rh_ctx_code
                        + lh_wm_code
                        + rh_wm_code
                    )
                    all_names = (
                        selected_fs_name
                        + lh_ctx_name
                        + rh_ctx_name
                        + lh_wm_name
                        + rh_wm_name
                    )
                    all_colors = (
                        selected_fs_color
                        + lh_ctx_color
                        + rh_ctx_color
                        + ilh_wm_color
                        + irh_wm_color
                    )

                # Save the color table
                tsv_df = pd.DataFrame(
                    {
                        "index": np.asarray(all_codes),
                        "name": all_names,
                        "color": all_colors,
                    }
                )

                if "tsv" in color_table:
                    out_file = out_vol.replace(".nii.gz", ".tsv")
                    cltparc.Parcellation.write_tsvtable(tsv_df, out_file, force=force)
                if "lut" in color_table:
                    out_file = out_vol.replace(".nii.gz", ".lut")

                    now = datetime.now()
                    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                    headerlines = [
                        "# $Id: {} {} \n".format(out_vol, date_time),
                        "{:<4} {:<50} {:>3} {:>3} {:>3} {:>3}".format(
                            "#No.", "Label Name:", "R", "G", "B", "A"
                        ),
                    ]

                    cltparc.Parcellation.write_luttable(
                        tsv_df["index"].tolist(),
                        tsv_df["name"].tolist(),
                        tsv_df["color"].tolist(),
                        out_file,
                        headerlines=headerlines,
                        force=force,
                    )

        elif os.path.isfile(out_vol) and not force:
            # Print a message
            if verbose:
                print(f"File {out_vol} already exists. Use force=True to overwrite it")

        return out_vol

    def conform2native(
        self,
        mgz_conform: str,
        nii_native: str,
        interp_method: str = "nearest",
        cont_tech: str = "local",
        cont_image: str = None,
        force: bool = False,
    ):
        """
        Moving image in comform space to native space

        Parameters:
        ----------
        mgz_conform : str
            Image in conform space

        nii_native : str
            Image in native space

        fssubj_dir : str
            FreeSurfer subjects directory

        fullid : str
            FreeSurfer ID

        interp_method: str
            Interpolation method ("nearest", "trilinear", "cubic")

        cont_tech : str
            Container technology ("singularity", "docker", "local")

        cont_image: str
            Container image to use

        force : bool
            Force the processing

        """
        raw_vol = os.path.join(self.subjs_dir, self.subj_id, "mri", "rawavg.mgz")
        tmp_raw = os.path.join(self.subjs_dir, self.subj_id, "tmp", "rawavg.nii.gz")

        # Get image dimensions
        if not os.path.isfile(raw_vol):
            raise FileNotFoundError(f"File {raw_vol} does not exist")

        cmd_bashargs = ["mri_convert", "-i", raw_vol, "-o", tmp_raw]
        cmd_cont = cltmisc.generate_container_command(
            cmd_bashargs, cont_tech, cont_image
        )  # Generating container command
        subprocess.run(
            cmd_cont, stdout=subprocess.PIPE, universal_newlines=True
        )  # Running container command

        img = nib.load(tmp_raw)
        tmp_raw_hd = img.header["dim"]

        # Remove tmp_raw
        os.remove(tmp_raw)

        if not os.path.isfile(nii_native) or force:
            # Moving the resulting parcellation from conform space to native
            raw_vol = os.path.join(self.subjs_dir, self.subj_id, "mri", "rawavg.mgz")

            cmd_bashargs = [
                "mri_vol2vol",
                "--mov",
                mgz_conform,
                "--targ",
                raw_vol,
                "--regheader",
                "--o",
                nii_native,
                "--no-save-reg",
                "--interp",
                interp_method,
            ]
            cmd_cont = cltmisc.generate_container_command(
                cmd_bashargs, cont_tech, cont_image
            )  # Generating container command
            subprocess.run(
                cmd_cont, stdout=subprocess.PIPE, universal_newlines=True
            )  # Running container command

        elif os.path.isfile(nii_native) and not force:
            # Print a message

            img = nib.load(nii_native)
            tmp_nii_hd = img.header["dim"]

            # Look if the dimensions are the same
            if all(tmp_raw_hd == tmp_nii_hd):
                print(f"File {nii_native} already exists and has the same dimensions")
                print(
                    f"File {nii_native} already exists. Use force=True to overwrite it"
                )

            else:
                cmd_bashargs = [
                    "mri_vol2vol",
                    "--mov",
                    mgz_conform,
                    "--targ",
                    raw_vol,
                    "--regheader",
                    "--o",
                    nii_native,
                    "--no-save-reg",
                    "--interp",
                    interp_method,
                ]
                cmd_cont = cltmisc.generate_container_command(
                    cmd_bashargs, cont_tech, cont_image
                )  # Generating container command
                subprocess.run(
                    cmd_cont, stdout=subprocess.PIPE, universal_newlines=True
                )  # Running container command

    def get_surface(self, hemi: str, surf_type: str):
        """
        This method returns the surface file according to the hemisphere and the surface type.

        Parameters
        ----------
        hemi: str        - Required  : Hemisphere (lh or rh):
        surf_type: str   - Required  : Surface type (pial, white, inflated, sphere):

        Returns
        -------
        surf_file: str : Surface file

        """

        if hemi not in ["lh", "rh"]:
            raise ValueError("The hemisphere must be lh or rh")

        if surf_type not in ["pial", "white", "inflated", "sphere"]:
            raise ValueError("The surface type must be pial, white, inflated or sphere")

        surf_file = self.fs_files["surf"][hemi]["mesh"][surf_type]

        return surf_file

    def get_vertexwise_map(self, hemi: str, map_type: str):
        """
        This method returns the vertexwise map file according to the hemisphere and the map type.

        Parameters
        ----------
        hemi: str        - Required  : Hemisphere (lh or rh):
        map_type: str    - Required  : Map type (curv, sulc, thickness, area, volume):

        Returns
        -------
        map_file: str : Vertexwise map file

        """

        if hemi not in ["lh", "rh"]:
            raise ValueError("The hemisphere must be lh or rh")

        if map_type not in ["curv", "sulc", "thickness", "area", "volume"]:
            raise ValueError(
                "The map type must be curv, sulc, thickness, area or volume"
            )

        map_file = self.fs_files["surf"][hemi]["map"][map_type]

        return map_file

    def get_annotation(self, hemi: str, annot_type: str):
        """
        This method returns the annotation file according to the hemisphere and the annotation type.

        Parameters
        ----------
        hemi: str        - Required  : Hemisphere (lh or rh):
        annot_type: str  - Required  : Annotation type (desikan, destrieux, dkt):

        Returns
        -------
        annot_file: str : Annotation file

        """

        if hemi not in ["lh", "rh"]:
            raise ValueError("The hemisphere must be lh or rh")

        if annot_type not in ["desikan", "destrieux", "dkt"]:
            raise ValueError("The annotation type must be desikan, destrieux or dkt")

        annot_file = self.fs_files["surf"][hemi]["parc"][annot_type]

        return annot_file


def create_fsaverage_links(
    fssubj_dir: str, fsavg_dir: str = None, refsubj_name: str = None
):
    """
    Create the links to the fsaverage folder

    Parameters
    ----------
        fssubj_dir     - Required  : FreeSurfer subjects directory. It does not have to match the $SUBJECTS_DIR environment variable:
        fsavg_dir      - Optional  : FreeSurfer fsaverage directory. If not provided, it will be extracted from the $FREESURFER_HOME environment variable:
        refsubj_name   - Optional  : Reference subject name. Default is None:

    Returns
    -------
    link_folder: str
        Path to the linked folder

    """

    # Verify if the FreeSurfer directory exists
    if not os.path.isdir(fssubj_dir):
        raise ValueError("The selected FreeSurfer directory does not exist")

    # Creating and veryfying the freesurfer directory for the reference name
    if fsavg_dir is None:
        if refsubj_name is None:
            fsavg_dir = os.path.join(
                os.environ["FREESURFER_HOME"], "subjects", "fsaverage"
            )
        else:
            fsavg_dir = os.path.join(
                os.environ["FREESURFER_HOME"], "subjects", refsubj_name
            )
    else:
        if fsavg_dir.endswith(os.path.sep):
            fsavg_dir = fsavg_dir[0:-1]

        if refsubj_name is not None:
            if not fsavg_dir.endswith(refsubj_name):
                fsavg_dir = os.path.join(fsavg_dir, refsubj_name)

    if not os.path.isdir(fsavg_dir):
        raise ValueError("The selected fsaverage directory does not exist")

    # Taking into account that the fsaverage folder could not be named fsaverage
    refsubj_name = os.path.basename(fsavg_dir)

    # Create the link to the fsaverage folder
    link_folder = os.path.join(fssubj_dir, refsubj_name)

    if not os.path.isdir(link_folder):
        process = subprocess.run(
            ["ln", "-s", fsavg_dir, fssubj_dir],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )

    return link_folder


def remove_fsaverage_links(linkavg_folder: str):
    """
    Remove the links to the average folder
    @params:
        linkavg_folder     - Required  : FreeSurfer average directory.
                                        It does not have to match the $SUBJECTS_DIR environment variable.
                                        If it is a link and do not match with the original fsaverage folder
                                        then it will be removed:
    """

    # FreeSurfer subjects directory
    fssubj_dir_orig = os.path.join(
        os.environ["FREESURFER_HOME"], "subjects", "fsaverage"
    )

    # if linkavg_folder is a link then remove it
    if (
        os.path.islink(linkavg_folder)
        and os.path.realpath(linkavg_folder) != fssubj_dir_orig
    ):
        os.remove(linkavg_folder)

def create_vertex_values(reg_values: np.ndarray, labels: np.ndarray, reg_ctable: np.ndarray) -> np.ndarray:
    """
    Create per-vertex values based on region labels and color table.
    
    Parameters
    ----------
    reg_values : np.ndarray
        Array of values for each region.

    labels : np.ndarray
        Array of region labels for each vertex.
        
    reg_ctable : np.ndarray
        Color table with shape (N, 5) where N is the number of regions.
        Each row contains RGB values and a region label in the last column.
        
    Returns
    -------
    vertex_values : np.ndarray
        Array of shape (num_vertices, 1) containing values for each vertex.
        Default value is 0 if no label matches.
    
    """
    
    # check that the number of rows of reg_values matches the number of regions in reg_ctable
    if  reg_values.shape[0] != reg_ctable.shape[0]:
        raise ValueError("The number of rows in reg_values must match the number of regions in reg_ctable")
    # Ensure reg_values is a 2D array
    if reg_values.ndim == 1:
        reg_values = reg_values.reshape(-1, 1)
    elif reg_values.ndim > 2:
        raise ValueError("reg_values must be a 1D or 2D array")

    n_cols = reg_values.shape[1]

    vertex_values = np.zeros((len(labels), n_cols), dtype=np.float32) # Default value is 0
    
    for i, region_info in enumerate(reg_ctable):
        # Find vertices with this label
        indices = np.where(labels == region_info[4])[0]
        
        # Assign the region color (RGB from first 3 columns)
        if len(indices) > 0:
            vertex_values[indices,:] = reg_values[i,:]
            
    return vertex_values


def create_vertex_colors(labels: np.ndarray, reg_ctable: np.ndarray) -> np.ndarray:
    """
    Create per-vertex colors based on region labels and color table.
    
    Parameters
    ----------
    labels : np.ndarray
        Array of region labels for each vertex.
        
    reg_ctable : np.ndarray
        Color table with shape (N, 5) where N is the number of regions.
        Each row contains RGB values and a region label in the last column.
        
    Returns
    -------
    vertex_colors : np.ndarray
        Array of shape (num_vertices, 3) containing RGB colors for each vertex.
        Default color is white (240, 240, 240) if no label matches.
    
    """
    
    vertex_colors = np.ones((len(labels), 3), dtype=np.uint8) * 240  # Default gray
    
    for i, region_info in enumerate(reg_ctable):
        # Find vertices with this label
        indices = np.where(labels == region_info[4])[0]
        
        # Assign the region color (RGB from first 3 columns)
        if len(indices) > 0:
            vertex_colors[indices, :3] = region_info[:3]
            
    return vertex_colors

def colors2colortable(colors: Union[list, np.ndarray]):
    """
    Convert a list of colors to a FreeSurfer color table

    Parameters
    ----------
        colors     - Required  : List of colors in hexadecimal format:

    Returns
    -------
    ctab: np.array
        FreeSurfer color table

    Usage
    -----
    >>> colors = ["#FF0000", "#00FF00", "#0000FF"]
    >>> ctab = colors2colortable(colors

    """

    if not isinstance(colors, (list, np.ndarray)):
        raise ValueError("The colors must be a list or a numpy array")

    if isinstance(colors, np.ndarray):
        colors = cltmisc.multi_rgb2hex(colors)

    # Create the new table
    ctab = np.array([[0, 0, 0, 0, 0]])
    for i, color in enumerate(colors):
        rgb = cltmisc.hex2rgb(color)
        vert_val = rgb[0] + rgb[1] * 2**8 + rgb[2] * 2**16

        # Concatenate the new table
        ctab = np.concatenate(
            (ctab, np.array([[rgb[0], rgb[1], rgb[2], 0, vert_val]])),
            axis=0,
        )

    # Remove the first row
    ctab = ctab[1:]

    return ctab


def detect_hemi(file_name: str):
    """
    Detect the hemisphere from the filename

    Parameters
    ----------
        file_name     - Required  : Filename:

    Returns
    -------
    hemi_cad: str : Hemisphere name

    """

    # Detecting the hemisphere
    surf_name = os.path.basename(file_name)
    file_name = surf_name.lower()

    # Find in the string annot_name if it is lh. or rh.
    if "lh." in surf_name:
        hemi = "lh"
    elif "rh." in surf_name:
        hemi = "rh"
    elif "hemi-" in surf_name:
        tmp_hemi = surf_name.split("-")[1].split("_")[0]
        tmp_ent = cltbids.str2entity(file_name)
        if "hemi" in tmp_ent.keys():
            tmp_hemi = tmp_ent["hemi"]

        if tmp_hemi in ["lh", "l", "left", "lefthemisphere"]:
            hemi = "lh"
        elif tmp_hemi in ["rh", "r", "right", "righthemisphere"]:
            hemi = "rh"
        else:
            hemi = None
            warnings.warn(
                "The hemisphere could not be extracted from the annot filename. Please provide it as an argument"
            )
    else:
        hemi = None
        warnings.warn(
            "The hemisphere could not be extracted from the annot filename. Please provide it as an argument"
        )

    return hemi


# Loading the JSON file containing the available parcellations
def load_lobes_json(lobes_json: str = None):
    """
    Load the JSON file containing the lobes definition.

    Parameters:
    ----------
    lobes_json : str
        JSON file containing the lobes definition.

    Returns:
    --------
    pipe_dict : dict
        Dictionary containing the default lobes definition.

    """

    # Get the absolute of this file
    if lobes_json is None:
        cwd = os.path.dirname(os.path.abspath(__file__))
        lobes_json = os.path.join(cwd, "config", "lobes.json")
    else:
        if not os.path.isfile(lobes_json):
            raise ValueError(
                "Please, provide a valid JSON file containing the lobes definition dictionary."
            )

    with open(lobes_json) as f:
        pipe_dict = json.load(f)

    return pipe_dict


def get_version(cont_tech: str = "local", cont_image: str = None):
    """
    Function to get the FreeSurfer version.

    Parameters
    ----------
    cont_tech    - Optional  : Container technology. Default is local:
    cont_image   - Optional  : Container image. Default is local:

    Output
    ------
    vers_cad: str : FreeSurfer version number

    """

    # Running the version command
    cmd_bashargs = ["recon-all", "-version"]
    cmd_cont = cltmisc.generate_container_command(
        cmd_bashargs, cont_tech, cont_image
    )  # Generating container command
    out_cmd = subprocess.run(cmd_cont, stdout=subprocess.PIPE, universal_newlines=True)

    for st_ver in out_cmd.stdout.split("-"):
        if "." in st_ver:
            vers_cad = st_ver
            break

    # Delete all the non numeric characters from the string except the "."
    vers_cad = "".join(filter(lambda x: x.isdigit() or x == ".", vers_cad))

    return vers_cad


def conform2native(
    cform_mgz: str,
    nat_nii: str,
    fssubj_dir: str,
    fullid: str,
    interp_method: str = "nearest",
    cont_tech: str = "local",
    cont_image: str = None,
):
    """
    Moving image in comform space to native space

    Parameters:
    ----------
    cform_mgz : str
        Image in conform space

    nat_nii : str
        Image in native space

    fssubj_dir : str
        FreeSurfer subjects directory

    fullid : str
        FreeSurfer ID

    interp_method: str
        Interpolation method ("nearest", "trilinear", "cubic")

    cont_tech : str
        Container technology ("singularity", "docker", "local")

    cont_image: str
        Container image to use

    """

    # Moving the resulting parcellation from conform space to native
    raw_vol = os.path.join(fssubj_dir, fullid, "mri", "rawavg.mgz")

    cmd_bashargs = [
        "mri_vol2vol",
        "--mov",
        cform_mgz,
        "--targ",
        raw_vol,
        "--regheader",
        "--o",
        nat_nii,
        "--no-save-reg",
        "--interp",
        interp_method,
    ]
    cmd_cont = cltmisc.generate_container_command(
        cmd_bashargs, cont_tech, cont_image
    )  # Generating container command
    subprocess.run(
        cmd_cont, stdout=subprocess.PIPE, universal_newlines=True
    )  # Running container command
