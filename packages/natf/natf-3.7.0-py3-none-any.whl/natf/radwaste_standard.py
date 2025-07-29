#!/usr/bin/env python3
# -*- coding:utf-8 -*-
''' class Radwaste.'''
import sys
import os
import numpy as np
import pandas as pd
import re
from natf import utils

if sys.version_info[0] > 2:
    basestring = str

thisdir = os.path.dirname(os.path.abspath(__file__))

# define radwaste classes to int dit
rwc2int = {'Clearance': 1, 'VLLW': 2, 'LLW': 3,
           'LLWC': 3, 'LLWB': 3, 'LLWA': 3,
           'ILW': 4, 'HLW': 5}


class RadwasteStandard(object):
    """Class Radwaste, used to store radioactive waste classification information"""

    def __init__(self, standard):
        self._standard = standard
        self._files = self.get_standard_default_files()
        self.get_dvalue_default_file()
        self._classes = []  # names of the different classes
        ######## D-VALUES #########
        self._dvalue_df = None
        self.read_standard()

    def get_standard_default_files(self):
        pass

    @property
    def standard(self):
        return self._standard

    @standard.setter
    def standard(self, value):
        if not isinstance(value, str):
            raise ValueError('standard must be a string!')
        if value not in ('CHN2018', 'USNRC', 'USNRC_FETTER', 'UK', 'RUSSIAN', 'FRANCE'):
            raise ValueError("standard {0} not supported!".format(value))
        self._standard = value

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, value):
        if not isinstance(value, list):
            raise ValueError("files must be a list!")
        for f in value:
            if not os.path.isfile(f):
                raise ValueError("File {0} not found".format(f))
        self._flies = value

    @property
    def classes(self):
        return self._classes

    @classes.setter
    def classes(self, value):
        if not isinstance(value, list):
            raise ValueError("classes must be a list!")
        for item in value:
            if not isinstance(item, str):
                raise ValueError("class name should be string")
        self._classes = value

    @property
    def dvalue_df(self):
        return self._dvalue_df

    @dvalue_df.setter
    def dvalue_df(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError("dvalue_df must be a dataframe.")
        self._dvalue_df = value

    def get_dvalue_default_file(self):
        """Get filename for d-values."""
        standard_dir = os.path.join(
            thisdir, "radwaste_standards", "D-VALUES")
        self._dvalue_file = os.path.join(standard_dir, "dvalues_iaea_2006.csv")

    def read_standard(self):
        """virtual function needs to be overwritten"""
        raise TypeError('you need to specify the exact standard')

    def get_nuc_dvalue_limits(self, nuc):
        """Get the dvalue limits for.

        Parameters:
        -----------
        nuc: string
            Nuclide name. Eg. H3, Cs137.

        Returns:
        --------
        Limit of the nuclide in specific material, unit [Bq].
        """
        col_num = len(self.dvalue_df.columns)
        limits = np.array(
            self.dvalue_df.loc[self.dvalue_df['Nuclide'] == nuc]).flatten()
        limits = limits[1:]
        # nuc not found in the list, set to default inf
        if len(limits) == 0:
            limits = np.array([float('inf')]*(col_num-1))
        return limits

    def get_nuc_limits(self, nuc, half_life=None, density=None):
        raise TypeError('you need to specify the exact standard')


class RadwasteStandardUK(RadwasteStandard):
    def __init__(self, standard):
        super().__init__(standard)

    def read_standard(self):
        """Read the csv into dataframe."""
        self._classes = ['Clearance', 'LLW', 'ILW', 'HLW']
        self._dvalue_df = read_dvalue_df_from_file(self._dvalue_file)

    def determine_class_uk(self, alpha_acts, acts, decay_heat, total_ci):
        """Determine the radwaste class UK, according to the alpha activity,
        total specific activity and the decay heat.

        Parameters:
        -----------
        alpha_acts: float
            Specific activity of alpha decay nuclides.
        acts: float
            Specific activity of all the nuclides.
        decay_heat: float
            Decay heat of a cooling time. Unit: kW/m3.
        """

        # input check
        if alpha_acts < 0 or acts < 0 or decay_heat < 0:
            raise ValueError(
                f"Negative data! Given: alpha_acts: {alpha_acts}, acts: {acts}, decay_heat: {decay_heat}")
        # if the decay heat is above 2kW/m3, it's HLW
        # if decay_heat > 2:
        #    return 'HLW'
        if total_ci <= 1.0:
            return 'Clearance'
        # if the decay heat is no more than 2kW/m3, check the alpha_acts and acts
        if alpha_acts <= 4.0e6 and (acts-alpha_acts) <= 1.2e7:
            return 'LLW'
        else:
            return 'ILW'


class RadwasteStandardChina(RadwasteStandard):
    def __init__(self, standard):
        # chn2018
        self._chn2018_df = None  # CHN2018 use
        super().__init__(standard)

    @property
    def chn2018_df(self):
        return self._chn2018_df

    @chn2018_df.setter
    def chn2018_df(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError("chn2018_df must be a dataframe.")
        self._chn2018_df = value

    def read_standard(self):
        """Read the csv into dataframe."""
        df = pd.read_csv(self.files[0])
        self._chn2018_df = df
        self._classes = self._chn2018_df.columns[1:]
        self._dvalue_df = read_dvalue_df_from_file(self._dvalue_file)

    def get_standard_default_files(self):
        files = []
        standard_dir = os.path.join(
            thisdir, "radwaste_standards", self.standard)
        files.append(os.path.join(standard_dir, self.standard + ".csv"))
        return files

    def get_nuc_limits(self, nuc, half_life=None, density=None):
        return self.get_nuc_limits_chn2018(nuc, half_life, density)

    def get_nuc_limits_chn2018(self, nuc, half_life=None, density=None):
        """Get the limits for different class of a specific nuclide.

        Parameters:
        -----------
        nuc: string
            Nuclide name. Eg. H3, Cs137.

        Returns:
        --------
        Limit of the nuclide in specific material, unit [Bq/kg].
        """
        col_num = len(self.chn2018_df.columns)
        limits = np.array(
            self.chn2018_df.loc[self.chn2018_df['Nuclide'] == nuc]).flatten()
        limits = limits[1:]
        # nuc not found in the list, set to default inf
        if len(limits) == 0:
            limits = np.array([float('inf')]*(col_num-1))
        return limits

    def determine_class_chn2018(self, indices, decay_heat):
        """Determine the radwaste class CHN2018, according to the indices and
        the decay heat.

        Parameters:
        -----------
        indices: numpy array (1D)
            Indices of difference class of a specific cooling time.
            Eg. clear index, VLLW index, ...
        decay_heat: float
            Decay heat of a cooling time. Unit: kW/m3.
        """

        # if the decay heat is above 2kW/m3, it's HLW
        # TODO: update the standard
        if decay_heat > 2 or indices[-1] > 1:
            return 'HLW'
        # if the decay heat is no more than 2kW/m3, check the indices
        # check indices length
        if len(indices) != len(self.chn2018_df.columns) - 1:
            raise ValueError("indices length wrong")
        for i in range(len(indices)):
            if indices[i] <= 1.0:
                return self.chn2018_df.columns[1+i]
        # not any index no more than 1, higher class
        return 'HLW'


class RadwasteStandardUS(RadwasteStandard):
    def __init__(self, standard):
        # usnrc
        self._dfl = None  # USNRC long live table use
        self._dfs = None  # USNRC short live table use
        self._df = None
        self._dfede = None  # USNRC
        super().__init__(standard)

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError("df must be a dataframe.")
        self._df = value

    @property
    def dfl(self):
        return self._dfl

    @dfl.setter
    def dfl(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError("dfl must be a dataframe.")
        self._dfl = value

    @property
    def dfs(self):
        return self._dfs

    @dfs.setter
    def dfs(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError("dfs must be a dataframe.")
        self._dfs = value

    @property
    def dfede(self):
        return self._dfede

    @dfede.setter
    def dfede(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError("dfede must be a dataframe.")
        self._dfede = value

    def read_standard(self):
        """Read the csv into dataframe."""
        if self.standard == 'USNRC':
            dfl = pd.read_csv(self.files[0])
            dfs = pd.read_csv(self.files[1])
            dfede = pd.read_csv(self.files[2])
            self._dfl = dfl
            self._dfs = dfs
            self._dfede = dfede
            self._classes = ['LLWA', 'LLWB', 'LLWC']
        elif self.standard == 'USNRC_FETTER':
            df = pd.read_csv(self.files[0])
            dfede = pd.read_csv(self.files[1])
            self._df = df
            self._dfede = dfede
            self._classes = ['LLWA', 'LLWB', 'LLWC']
        self._dvalue_df = read_dvalue_df_from_file(self._dvalue_file)

    def get_nuc_limits(self, nuc, half_life=None, density=None):
        if self.standard == 'USNRC':
            return self.get_nuc_limits_usnrc(nuc, half_life, density)
        # USNRC_FETTER standard
        elif self.standard == 'USNRC_FETTER':
            return self.get_nuc_limits_usnrc_fetter(nuc, half_life, density)

    def get_standard_default_files(self):
        """Get filename for specific standard."""
        files = []
        standard_dir = os.path.join(
            thisdir, "radwaste_standards", self.standard)
        if self.standard == 'USNRC':
            # long live table
            files.append(os.path.join(
                standard_dir, self._standard + "_LL.csv"))
            # short live table
            files.append(os.path.join(
                standard_dir, self._standard + "_SL.csv"))
            # EDE table
            files.append(os.path.join(standard_dir,
                                      self._standard + "_EDE_MASS.csv"))
        elif self.standard == 'USNRC_FETTER':
            files.append(os.path.join(standard_dir, self._standard + ".csv"))
            # EDE table
            files.append(os.path.join(os.path.join(thisdir, "radwaste_standards", "USNRC"),
                                      "USNRC_EDE_MASS.csv"))
        return files

    def get_nuc_limits_usnrc_fetter(self, nuc, half_life, density):
        """Get the limits for different class of a specific nuclide.

        Parameters:
        -----------
        nuc: string
            Nuclide name. Eg. H3, Cs137.
        half_life: float
            Half life of the nuclide, unit: [s].
        density: float
            Density of the material where the nuclide exists, unit: [g/cm3].
            Required in 'USNRC' and 'USNRC_FETTER' standard because of the
            unit conversion.

        Returns:
        --------
        Limit of the nuclide in specific material, unit [Bq/kg].
        """

        # check density
        if density is None:
            raise ValueError("Density must be provide in 'USNRC_FETTER'")
        if half_life < 3600.0*24*365.25*5:
            limits = np.array([700.0, 700.0, 700.0])
            # convert from Ci/m3 to Bq/kg
            limits = np.multiply(limits, utils.ci2bq(1.0)/density/1e3)
        else:
            limits_s = np.array(
                self.df.loc[self.df['Nuclide'] == nuc]).flatten()
            if len(limits_s) > 1:
                limit_c = convert_nrc_fetter_limit(
                    limits_s[-1], density=density)
                limits = [limit_c*0.01, limit_c*0.1, limit_c]
            else:
                # nuc not in table
                limits = [float('inf'), float('inf'), float('inf')]
        return limits

    def get_nuc_limit_usnrc_clearance(self, nuc, material_type='Steel'):
        """Get the limits for different class of a specific nuclide.

        Parameters:
        -----------
        nuc: string
            Nuclide name. Eg. H3, Cs137.
        material_type: string
            The material type. Nuclide in different types of materials has
            different EDE values. Therefore, the material type should be
            provided. The default material type is set to Steel.

        Returns:
        --------
        Clearance limit of the nuclide in specific nuclide, unit [Bq/kg].
        """

        edes = np.array(self.dfede.loc[self.dfede['Nuclide'] == nuc]).flatten()
        if len(edes) == 0:  # nuc not in the list
            return float('inf')  # set to inf as default
        ede = edes[1]  # [uSv/hr per Bq/g]
        limit = 10 * 1e3 / ede  # [Bq/kg]
        return limit

    def get_nuc_limits_usnrc(self, nuc, half_life, density):
        """Get the limits for different class of a specific nuclide.

        Parameters:
        -----------
        nuc: string
            Nuclide name. Eg. H3, Cs137.
        half_life: float
            Half life of the nuclide, unit: [s].
        density: float
            Density of the material where the nuclide exists, unit: [g/cm3].
            Required in 'USNRC' and 'USNRC_FETTER' standard because of the
            unit conversion.

        Returns:
        --------
        Limit of the nuclide in specific material, unit [Bq/kg].
        """

        # check if the half life provided
        if half_life is None:
            raise ValueError("Half of the nuclide must be provided in "
                             "USNRC standard")

        if nuc in ('Pu241', 'Cm242') or (not utils.is_short_live(half_life)):
            # long lvie nuclide or Pu242/Cm242
            col_num = len(self.dfl.columns)
            # use data from USNRC_LL
            limits = np.array(
                self.dfl.loc[self.dfl['Nuclide'] == nuc]).flatten()
            limits = limits[1:]
        else:
            #  short-live
            col_num = len(self.dfs.columns)
            # use data from USNRC_SL
            if half_life < 3600.0*24*365.25*5:
                limits = np.array([700.0, 700.0, 700.0])
            else:
                limits = np.array(
                    self.dfs.loc[self.dfs['Nuclide'] == nuc]).flatten()
                limits = limits[1:]

        # convert the unit from Ci/m3 or Ci/g to Bq/kg
        if nuc in ('Pu241', 'Cm242'):
            # convert from Ci/g to Bq/kg
            limits = np.multiply(limits, utils.ci2bq(1.0)*1e3)
        else:
            # convert from Ci/m3 to Bq/kg
            limits = np.multiply(limits, utils.ci2bq(1.0)/density/1e3)

        # nuc not found in the list, set to default inf
        if len(limits) == 0:
            limits = np.array([float('inf')]*(col_num-1))
        return limits

    def determine_class(self, *args):
        if self.standard == 'USNRC':
            return self.determine_class_usnrc(*args)
        # USNRC_FETTER standard
        elif self.standard == 'USNRC_FETTER':
            return self.determine_class_usnrc_fetter(*args)

    def determine_class_usnrc_fetter(self, rwi, ci):
        """Determine the radwaste class USNRC, according to the rw.

        Parameters:
        -----------
        rwi: numpy array (1D)
            Indices of difference class of a specific cooling time.
        ci: int
            Clearance index under USNRC standard.
        """

        # Clearance if ci <= 1
        if ci <= 1.0:
            return 'Clearance'

        classes = ['LLWA', 'LLWB', 'LLWC']
        # class according to rwi_ll
        for i in range(len(rwi)):
            if rwi[i] <= 1.0:
                return classes[i]

        # all rwi bigger than 1
        return 'ILW'

    def determine_class_usnrc(self, rwi_ll, rwi_sl, ci):
        """Determine the radwaste class USNRC, according to the rw.

        Parameters:
        -----------
        rwi_ll: numpy array (1D)
            Indices of difference class of a specific cooling time for long
            lived nuclides and Pu241 and Cm242.
            Eg. LLWA, LLWB, LLWC, ILW
        rwi_sl: numpy array (1D)
            Indices of difference class of a specific cooling time for short
            lived nuclides.
        ci: int
            Clearance index under USNRC standard.
        """

        # Clearance if ci <= 1
        if ci <= 1.0:
            return 'Clearance'

        classes = ['LLWA', 'LLWB', 'LLWC', 'ILW']
        # check indices length
        if len(rwi_ll) != len(self.dfl.columns) - 1 or \
                (len(rwi_sl) != len(self.dfl.columns) - 1):
            raise ValueError("radwaste indices length wrong")

        class_ll, class_sl, class_al = 3, 3, 3
        # class according to rwi_ll
        for i in range(len(rwi_ll)):
            if rwi_ll[i] <= 1.0:
                class_ll = i
                break
        # class according to rwi_sl
        for i in range(len(rwi_sl)):
            if rwi_sl[i] <= 1.0:
                class_sl = i
                break

        # combine two class
        if class_ll == 0:
            class_al = class_sl
        elif class_ll > 0 and class_ll <= 2:
            if class_sl <= 2:
                class_al = 2

        return classes[class_al]


class RadwasteStandardRussia(RadwasteStandard):
    def __init__(self, standard):
        self._df = None  # RUSSIAN use
        super().__init__(standard)

    def read_standard(self):
        """Read the csv into dataframe."""
        self._classes = ['LLW', 'ILW']
        self._df = pd.read_csv(self.files[0])
        self._dvalue_df = read_dvalue_df_from_file(self._dvalue_file)

    def get_standard_default_files(self):
        """Get filename for specific standard."""
        files = []
        standard_dir = os.path.join(
            thisdir, "radwaste_standards", self.standard)
        files.append(os.path.join(standard_dir, self._standard + ".csv"))
        return files

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError("df must be a dataframe.")
        self._df = value

    def get_nuc_limits(self, nuc, half_life=None, density=None):
        """Get the limits for different class of a specific nuclide.

        Parameters:
        -----------
        nuc: string
            Nuclide name. Eg. H3, Cs137.
        half_life: float
            Half life of the nuclide, unit: [s].

        Returns:
        --------
        Limit of the nuclide in specific material, unit [Bq/kg].
        """

        if half_life is not None:
            if utils.is_short_live(half_life, threshold=5):
                limits = [float('inf')]
                return limits
        else:
            # read table first
            limits = np.array(self.df.loc[self.df['Nuclide'] == nuc]).flatten()
            limits = limits[1:]
            if len(limits) == 0:
                # nuc not in table
                if is_u(nuc) or is_alpha_5(nuc):
                    limits = [3.7e6]
                else:
                    limits = [float('inf')]
            else:
                return limits
        return limits

    def determine_class_russian(self, indices):
        """Determine the radwaste class RUSSIAN, according to the indices.

        Parameters:
        -----------
        indices: numpy array (1D)
            Indices of difference class of a specific cooling time.
            Eg. clear index, LLW index, ...
        """

        # check indices length
        if len(indices) != len(self.df.columns) - 1:
            raise ValueError("indices length wrong")
        for i in range(len(indices)):
            if indices[i] <= 1.0:
                return self.df.columns[1+i]
        # not any index no more than 1, higher class
        return 'ILW'


class RadwasteStandardFrance(RadwasteStandard):
    """French radwaste standard with IRAS (Radiological Index for Disposal Acceptance) calculation."""

    def __init__(self, standard):
        self._tfa_df = None  # FRANCE TFA use
        super().__init__(standard)

    @property
    def tfa_df(self):
        return self._tfa_df

    @tfa_df.setter
    def tfa_df(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError("tfa_df must be a dataframe.")
        self._tfa_df = value

    def read_standard(self):
        """Read the TFA.csv into dataframe."""
        self._classes = ['TFA', 'Type-A',
                         'Type-B']  # French standard classifications
        self._tfa_df = pd.read_csv(self.files[0])
        # Clean up the dataframe - fix column names and handle data issues
        self._tfa_df.columns = [
            'Nuclide', 'Halflife(y)', 'ClassTFA', 'DeclearationThreshold(Bq/g)', 'LumpDeclearationLimit(Bq/g)']
        # Remove empty rows
        self._tfa_df = self._tfa_df.dropna(subset=['Nuclide'])
        # Fix some data formatting issues in the original file
        self._tfa_df['ClassTFA'] = pd.to_numeric(
            self._tfa_df['ClassTFA'], errors='coerce')
        self._tfa_df['DeclearationThreshold(Bq/g)'] = pd.to_numeric(
            self._tfa_df['DeclearationThreshold(Bq/g)'], errors='coerce')
        self._tfa_df['LumpDeclearationLimit(Bq/g)'] = pd.to_numeric(
            self._tfa_df['LumpDeclearationLimit(Bq/g)'], errors='coerce')
        self._tfa_df = self._tfa_df.dropna(subset=['ClassTFA'])

        # Convert thresholds from Bq/g to Bq/kg for consistency with internal units
        # Multiply by 1000 to convert from Bq/g to Bq/kg
        self._tfa_df['DeclearationThreshold(Bq/kg)'] = self._tfa_df['DeclearationThreshold(Bq/g)'] * 1000.0
        self._tfa_df['LumpDeclearationLimit(Bq/kg)'] = self._tfa_df['LumpDeclearationLimit(Bq/g)'] * 1000.0

        self._dvalue_df = read_dvalue_df_from_file(self._dvalue_file)

    def get_standard_default_files(self):
        """Get filename for French standard."""
        files = []
        standard_dir = os.path.join(
            thisdir, "radwaste_standards", self.standard)
        files.append(os.path.join(standard_dir, "TFA.csv"))
        return files

    def get_nuc_limits(self, nuc, half_life=None, density=None):
        """Get the TFA class and thresholds for a specific nuclide.

        Parameters:
        -----------
        nuc: string
            Nuclide name. Eg. H3, Cs137.
        half_life: float
            Half life of the nuclide, unit: [s]. (Not used in French standard)
        density: float
            Density of the material, unit: [g/cm3]. (Not used in French standard)

        Returns:
        --------
        Dictionary containing TFA class and threshold limits in Bq/kg.
        """
        if self._tfa_df is None:
            return {'class': None, 'declaration_threshold': float('inf'), 'lump_limit': float('inf')}

        nuc_data = self._tfa_df.loc[self._tfa_df['Nuclide'] == nuc]
        if len(nuc_data) == 0:
            # Nuclide not found in TFA table
            return {'class': None, 'declaration_threshold': float('inf'), 'lump_limit': float('inf')}

        nuc_row = nuc_data.iloc[0]
        return {
            'class': nuc_row['ClassTFA'],
            'declaration_threshold': nuc_row['DeclearationThreshold(Bq/kg)'],
            'lump_limit': nuc_row['LumpDeclearationLimit(Bq/kg)']
        }

    def get_nuc_tfa_class(self, nuc):
        """Get the TFA class for a specific nuclide.

        Parameters:
        -----------
        nuc: string
            Nuclide name. Eg. H3, Cs137.

        Returns:
        --------
        TFA class (0, 1, 2, or 3) or None if nuclide not found.
        """
        if self._tfa_df is None:
            return None

        nuc_data = self._tfa_df.loc[self._tfa_df['Nuclide'] == nuc]
        if len(nuc_data) == 0:
            return None
        return nuc_data.iloc[0]['ClassTFA']

    def calculate_iras(self, nuclide_activities):
        """Calculate IRAS (Radiological Index for Disposal Acceptance).

        The IRAS for France standard is calculated by sum of Ai/10^Ci, where:
        - Ai is the specific activity of radionuclide i (Bq/g)
        - Ci is the class of radionuclide (0, 1, 2, 3) from TFA.csv

        Parameters:
        -----------
        nuclide_activities: dict
            Dictionary with nuclide names as keys and specific activities (Bq/kg) as values.

        Returns:
        --------
        float: IRAS value
        """
        iras = 0.0

        for nuc, activity_bq_kg in nuclide_activities.items():
            if activity_bq_kg <= 0:
                continue

            tfa_class = self.get_nuc_tfa_class(nuc)
            if tfa_class is None:
                # Nuclide not in TFA table - skip or use default class
                continue

            # Convert activity from Bq/kg to Bq/g for IRAS formula
            activity_bq_g = activity_bq_kg / 1000.0

            # IRAS formula: sum of Ai/10^Ci
            iras += activity_bq_g / (10 ** tfa_class)

        return iras

    def determine_class_france(self, iras_value, contact_dose=None, specific_activity=None):
        """Determine the radwaste class based on IRAS value, contact dose, and specific activity.

        Parameters:
        -----------
        iras_value: float
            Calculated IRAS value.
        contact_dose: float, optional
            Contact dose rate in µSv/h. Required when IRAS > 1 for proper classification.
        specific_activity: float, optional
            Total specific activity in Bq/kg. If > 2.5E8 Bq/kg (2.5E5 Bq/g), waste is Type-B.

        Returns:
        --------
        string: Radwaste classification ('TFA', 'Type-A', or 'Type-B').

        Notes:
        ------
        In France, there is no clearance concept. All material in nuclear facilities
        is treated as radwaste when classified. The classification is:
        - IRAS <= 1: TFA (Très Faible Activité - Very Low Activity)
        - IRAS > 1 and contact_dose < 100 µSv/h: Type-A waste
        - IRAS > 1 and contact_dose >= 100 µSv/h: Type-B waste
        - specific_activity > 2.5E8 Bq/kg: Type-B waste (overrides other criteria)
        """
        # Check specific activity first - overrides other criteria
        # Convert the threshold from 2.5E5 Bq/g to 2.5E8 Bq/kg
        if specific_activity is not None and specific_activity > 2.5e8:
            return 'Type-B'
            return 'Type-B'

        if iras_value <= 1.0:
            return 'TFA'
        else:
            # For IRAS > 1, contact dose is needed for proper classification
            if contact_dose is None:
                # If contact dose not provided, assume worst case (Type-B)
                # In practice, contact dose should always be provided for proper classification
                return 'Type-B'
            elif contact_dose < 100.0:  # µSv/h
                return 'Type-A'
            else:  # contact_dose >= 100.0 µSv/h
                return 'Type-B'


def convert_nrc_fetter_limit(limit_cs, density):
    """
    Convert the NRC_FETTER limit from string to a float.
    """
    if limit_cs == 'TMSA':
        limit_c = float('inf')
        return limit_c

    tokens = limit_cs.strip().split()
    if len(tokens) == 1:
        value = float(limit_cs)  # unit Ci/m3
        limit_c = utils.ci2bq(value) / density / 1e3  # unit: Bq/kg
        return limit_c

    if len(tokens) == 2:
        value = float(tokens[0])
        unit = tokens[1]  # unit is  (nCi/g)
        limit_c = 1e-9 * utils.ci2bq(value) * 1e3  # unit: Bq/kg
        return limit_c

    # unknown limit_cs
    raise ValueError("limit_cs {0} format wrong".format(limit_cs))


def rwc_to_int(rwc, standard='CHN2018'):
    """Convert rwc to int."""
    if standard == 'CHN2018':
        rwc2inp = {'Clearance': 1, 'VLLW': 2, 'LLW': 3, 'ILW': 4, 'HLW': 5}
    elif standard in ['USNRC', 'USNRC_FETTER']:
        rwc2inp = {'Clearance': 1, 'LLWA': 3,
                   'LLWB': 3, 'LLWC': 3, 'ILW': 4, 'HLW': 5}
    elif standard == 'RUSSIAN':
        rwc2inp = {'LLW': 3, 'ILW': 4, 'HLW': 5}
    elif standard == 'UK':
        rwc2inp = {'Clearance': 1, 'LLW': 3, 'ILW': 4, 'HLW': 5}
    elif standard == 'FRANCE':
        # French standard only has TFA, Type-A, and Type-B
        # No clearance concept - all material in nuclear facilities is radwaste
        rwc2inp = {'TFA': 2, 'Type-A': 3, 'Type-B': 4}
    else:
        raise ValueError(f"standard: {standard} not supported")
    return rwc2inp[rwc]


def ctr_to_int(ctr):
    """Convert cooling time requirement to int."""
    # convert ctr to float
    if '<' in ctr:
        ctr = float(ctr[1:]) * 0.99
    elif '>' in ctr:
        ctr = float(ctr[1:]) * 1.01
    else:
        ctr = float(ctr)

    # check ctr
    if ctr <= 1:  # green
        return 1
    elif 1 < ctr and ctr <= 10:  # blue
        return 2
    elif 10 < ctr and ctr <= 100:  # yellow
        return 3
    elif 100 < ctr and ctr <= 1000:  # pink
        return 4
    elif 1000 < ctr:  # red
        return 5
    else:
        raise ValueError(f"Wrong ctr: {ctr}")


def is_u(nuc):
    """Check whether a nuclide is U"""
    u_pattern = re.compile("^U[0-9]*", re.IGNORECASE)
    if re.match(u_pattern, nuc):
        return True
    else:
        return False


def is_alpha_5(nuc):
    """Check whether a nuclide is alpha emitting and half-life > 5 year"""
    alpha_5_nucs = ('Np237', 'Pu238', 'Pu239', 'Pu240', 'Pu241', 'Pu242', 'Pu244',
                    'Am241', 'Am242m', 'Am243', 'Cm243', 'Cm244', 'Cm245', 'Cm246',
                    'Cm247', 'Cm248', 'Cf249', 'Cf250', 'Cf251')
    if nuc in alpha_5_nucs:
        return True
    else:
        return False


def read_dvalue_df_from_file(filename):
    """Read d-values from file"""
    dvalue_df = pd.read_csv(filename)
    dvalue_df['Dvalue(TBq)'] = dvalue_df['Dvalue(TBq)'].replace(
        ['UL'], 'inf').astype('float').multiply(1e9)
    dvalue_df['D1value(TBq)'] = dvalue_df['D1value(TBq)'].replace(
        ['UL'], 'inf').astype('float').multiply(1e9)
    dvalue_df['D2value(TBq)'] = dvalue_df['D2value(TBq)'].replace(
        ['UL'], 'inf').astype('float').multiply(1e9)
    # convert from TBq to Bq

    return dvalue_df
