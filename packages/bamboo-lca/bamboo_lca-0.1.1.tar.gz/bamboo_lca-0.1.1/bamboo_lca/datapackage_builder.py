import bw_processing as bwp
from scipy import sparse
import pandas as pd
import numpy as np
from typing import List, Tuple, Any


class DatapackageBuilder:
    def prepare_dp_matrix(self, tech_matrix, bio_matrix, cf_matrix):
        """
        Transform matrices data to bw matrices data, ready for the datapackages.
        """
        tech_sparse = sparse.coo_array(tech_matrix)
        tech_coors = np.column_stack(tech_sparse.nonzero())
        
        max_coor = tech_coors[np.argmax(np.sum(tech_coors, axis=1))]
        tech_data = tech_sparse.data
        tech_indices = np.array([tuple(coor) for coor in tech_coors], dtype=bwp.INDICES_DTYPE)
        tech_flip = np.array([False if i[0] == i[1] else True for i in tech_indices])

        bio_sparse = sparse.coo_array(bio_matrix)
        bio_coors = np.column_stack(bio_sparse.nonzero())
        bio_data = bio_sparse.data
        bio_indices = np.array([tuple([coord[0] + max_coor[0] + 1, coord[1]]) for coord in bio_coors], dtype=bwp.INDICES_DTYPE)
        
        cf_sparse = sparse.coo_array(cf_matrix)
        cf_coors = np.column_stack(cf_sparse.nonzero())
        cf_data =  cf_sparse.data
        cf_indices = np.array([tuple([coord[0] + max_coor[0] + 1, coord[1] + max_coor[1] + 1]) for coord in cf_coors], dtype=bwp.INDICES_DTYPE)

        return [
            (tech_data, tech_indices, tech_flip),
            (bio_data, bio_indices),
            (cf_data, cf_indices)
        ]

    def prepare_datapackage(self, datapackage_data: List[Tuple[Any, ...]], uncertainty: list = None):
        """
        Prepare datapackage for brightway LCA calculation.

        Parameters:
            * datapackage_data: A list of tuple includes all information to create a datapackage.
            * uncertainty: The uncertainty for all matrices.
        """
        tech_data, tech_indices, tech_flip = datapackage_data[0]
        bio_data, bio_indices = datapackage_data[1]
        cf_data, cf_indices = datapackage_data[2]
        if uncertainty is None:
            tech_uncertainty, bio_uncertainty, cf_uncerainty = None, None, None
        else:
            tech_uncertainty, bio_uncertainty, cf_uncerainty = uncertainty[0], uncertainty[1], uncertainty[2]

        dp = bwp.create_datapackage()
        dp.add_persistent_vector(
            matrix='technosphere_matrix',
            indices_array=tech_indices,
            data_array=tech_data,
            flip_array=tech_flip,
            distributions_array=tech_uncertainty,
        )
        dp.add_persistent_vector(
            matrix='biosphere_matrix',
            indices_array=bio_indices,
            data_array=bio_data,
            distributions_array=bio_uncertainty,
        )
        dp.add_persistent_vector(
            matrix='characterization_matrix',
            indices_array=cf_indices,
            data_array=cf_data,
            distributions_array=cf_uncerainty,
        )

        return dp