# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of an Optimistic Estimate of the Piatetsky-Shapiro quality measure.
"""

from subgroups.quality_measures.quality_measure import QualityMeasure
from subgroups.exceptions import SubgroupParameterNotFoundError
from subgroups.quality_measures.piatetsky_shapiro import PiatetskyShapiro

# Python annotations.
from typing import Union

class PiatetskyShapiroOptimisticEstimate2(QualityMeasure): # SOURCE: https://link.springer.com/chapter/10.1007%2F978-3-540-87479-9_47
    """This class defines an Optimistic Estimate of the Piatetsky-Shapiro quality measure.
    """
    
    _singleton = None
    __slots__ = ()
    
    def __new__(cls) -> 'PiatetskyShapiroOptimisticEstimate2':
        if PiatetskyShapiroOptimisticEstimate2._singleton is None:
            PiatetskyShapiroOptimisticEstimate2._singleton = object().__new__(cls)
        return PiatetskyShapiroOptimisticEstimate2._singleton
    
    def compute(self, dict_of_parameters : dict[str, Union[int, float]]) -> float:
        """Method to compute the PiatetskyShapiroOptimisticEstimate2 quality measure (you can also call to the instance for this purpose).
        
        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this quality measure.
        :return: the computed value for the PiatetskyShapiroOptimisticEstimate2 quality measure.
        """
        if type(dict_of_parameters) is not dict:
            raise TypeError("The type of the parameter 'dict_of_parameters' must be 'dict'.")
        if (QualityMeasure.TRUE_POSITIVES not in dict_of_parameters):
            raise SubgroupParameterNotFoundError("The subgroup parameter 'tp' is not in 'dict_of_parameters'.")
        if (QualityMeasure.TRUE_POPULATION not in dict_of_parameters):
            raise SubgroupParameterNotFoundError("The subgroup parameter 'TP' is not in 'dict_of_parameters'.")
        if (QualityMeasure.FALSE_POPULATION not in dict_of_parameters):
            raise SubgroupParameterNotFoundError("The subgroup parameter 'FP' is not in 'dict_of_parameters'.")
        tp = dict_of_parameters[QualityMeasure.TRUE_POSITIVES]
        TP = dict_of_parameters[QualityMeasure.TRUE_POPULATION]
        FP = dict_of_parameters[QualityMeasure.FALSE_POPULATION]
        return tp * ( 1 - ( TP / (TP+FP) ) ) # n * p * (1 - p0) = tp * (1 - p0)
    
    def get_name(self) -> str:
        """Method to get the quality measure name (equal to the class name).
        """
        return "PiatetskyShapiroOptimisticEstimate2"
    
    def optimistic_estimate_of(self) -> dict[str, QualityMeasure]:
        """Method to get a python dictionary with the quality measures of which this one is an optimistic estimate.
        
        :return: a python dictionary in which the keys are the quality measure names and the values are the instances of those quality measures.
        """
        return dict({PiatetskyShapiro().get_name() : PiatetskyShapiro()})
    
    def __call__(self, dict_of_parameters : dict[str, Union[int, float]]) -> float:
        """Compute the PiatetskyShapiroOptimisticEstimate2 quality measure.
        
        :param dict_of_parameters: python dictionary which contains all the needed parameters with which to compute this quality measure.
        :return: the computed value for the PiatetskyShapiroOptimisticEstimate2 quality measure.
        """
        return self.compute(dict_of_parameters)
