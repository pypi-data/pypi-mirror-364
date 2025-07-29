#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import configparser
import numpy as np
import pandas as pd
import os
import shutil
from natf.cell import Cell, is_item_cell
from natf.part import Part, is_item_part
from natf.radwaste_standard import RadwasteStandardChina, RadwasteStandardUK, RadwasteStandardUS, RadwasteStandardRussia, RadwasteStandardFrance
from natf import utils, nuc_treat
from natf.fispact_output import get_interval_list

# global variables
SUPPORTED_NUC_SETS = ('FENDL3', 'TENDL2019')
SUPPORTED_RADWASTE_STANDARDS = (
    'CHN2018', 'UK', 'USNRC', 'USNRC_FETTER', 'RUSSIAN', 'FRANCE')
SUPPORTED_AIMS = ('CELL_ACT_PRE', 'CELL_ACT_POST',
                  'CELL_DPA_PRE', 'CELL_DPA_POST',
                  'COOLANT_ACT_PRE', 'COOLANT_ACT_POST',
                  'CELL_RWC_VIS', 'CELL_MAT_EVO', 'CELL_SPLIT', 'CELL_TALLY_PARSE')
SUPPORTED_N_GROUP_SIZE = (69, 175, 315, 709)


def get_work_dir(config_file, config=None):
    """Get the working directory of the natf"""
    config_dir = os.path.dirname(config_file)
    if config is None:
        config = configparser.ConfigParser()
        config.read(config_file)
    work_dir = config.get('general', 'work_dir', fallback=config_dir)
    if work_dir == '.':
        work_dir = config_dir
    return work_dir


def get_ndose_dist(config_file=None, config=None):
    """
    Get the dose distribution parameters from the configuration file.

    Args:
        config_file (str): Path to the configuration file.
        config (configparser.ConfigParser, optional): ConfigParser object. If None, a new ConfigParser will be created and the config_file will be read.

    Returns:
        tuple: A tuple containing:
            - ndose (int or None): The number of doses. None if not found or invalid.
            - dist (float or None): The dose distribution value. None if not found, invalid, or if ndose is a single value.
    """
    """Get the working directory of the natf"""
    ndose, dist = None, None
    if config is None:
        config = configparser.ConfigParser()
        config.read(config_file)
    if config.has_option('fispact', 'dose'):
        dose = config.get('fispact', 'dose')
        if dose:
            tokens = dose.split()
            if len(tokens) == 1:
                ndose = int(tokens[0])
                if ndose != 1:
                    raise ValueError(
                        "dose parameter not valid, check fispact manual")
            elif len(tokens) == 2:
                ndose = int(tokens[0])
                dist = float(tokens[1])
                if ndose != 2:
                    raise ValueError(
                        "dose parameter not valid, check fispact manual")
                if dist < 0.3:
                    raise ValueError(
                        "distance must large than 0.3 m from point source model")
            else:
                raise ValueError(
                    "dose parameter not valid, check fispact manual")
    return ndose, dist


@utils.log
def check_config(filename="config.ini"):
    """Read the 'config.ini' file and check the variables.
    if the required variable is not given, this function will give error
    message."""

    config = configparser.ConfigParser()
    config.read(filename)
    # general
    work_dir = get_work_dir(filename, config=config)
    aim = config.get('general', 'aim')
    # check the input variables
    if aim not in SUPPORTED_AIMS:  # check aim validate
        raise ValueError(f"aim: {aim} not supported")

    # mcnp
    mcnp_input = os.path.join(work_dir, config.get('mcnp', 'mcnp_input'))
    mcnp_output = os.path.join(work_dir, config.get('mcnp', 'mcnp_output'))
    continue_output = config.get('mcnp', 'continue_output', fallback='')
    if continue_output:
        #        continue_output = os.path.join(work_dir, continue_output)
        continue_output = utils.valid_input_file(
            os.path.join(work_dir, continue_output), continue_output)

    # mcnp.n_group_size
    if aim in ('CELL_ACT_PRE', 'CELL_ACT_POST',
               'COOLANT_ACT_PRE', 'COOLANT_ACT_POST',
               'CELL_RWC_VIS', 'CELL_MAT_EVO'):
        n_group_size = config.getint('mcnp', 'n_group_size')
        if n_group_size not in SUPPORTED_N_GROUP_SIZE:
            raise ValueError('n_group_size must be ', SUPPORTED_N_GROUP_SIZE)
    if aim in ('CELL_TALLY_PARSE'):
        n_group_size = config.getint('mcnp', 'n_group_size')
    if aim in ['CELL_DPA_PRE', 'CELL_DPA_POST']:
        n_group_size = config.getint('mcnp', 'n_group_size')
        if n_group_size != 709:
            raise ValueError(
                'n_group_size must be 709 if you want to calculate DPA')

    # mcnp.tally_numbers
    # check deprecated keyword tally_number
    try:
        item = config.get('mcnp', 'tally_number')
    except:
        pass
    else:
        raise ValueError(
            f"DEPRECATED KEYWORD: the keyword 'TALLY_NUMBER' has changed to 'TALLY_NUMBERS'")
    if aim in ('CELL_ACT_PRE', 'CELL_ACT_POST',
               'CELL_DPA_PRE', 'CELL_DPA_POST',
               'COOLANT_ACT_PRE', 'COOLANT_ACT_POST',
               'CELL_RWC_VIS', 'CELL_MAT_EVO', 'CELL_TALLY_PARSE'):
        tally_property = get_tally_property(config)
        tally_numbers = get_tally_numbers(config)
        tally_unit = get_tally_unit(config)

    # mcnp.nuclide_sets
    # deprecated key words check
    try:
        tokens = config.get('mcnp', 'nuclide_set').split(',')
    except:
        pass
    else:
        raise ValueError(
            f"Keyword 'NUCLIDE_SET' is deprecated, use 'NUCLIDE_SETS'")
    nuclide_sets = None
    if aim == 'CELL_MAT_EVO':
        nuclide_sets = get_nuclide_sets(config)

    # coolant_flow, available only for COOLANT_ACT mode
    if aim in ['COOLANT_ACT_PRE', 'COOLANT_ACT_POST']:
        # coolant_flow.coolant_flow_parameters, required in COOLANT_ACT mode
        coolant_flow_parameters = os.path.join(work_dir,
                                               config.get('coolant_flow', 'coolant_flow_parameters'))
        if aim in ['COOLANT_ACT_PRE', 'COOLANT_ACT_POST'] and coolant_flow_parameters is None:
            raise ValueError(
                "coolant_flow_parameters must be provided in COOLANT_ACT mode")
        # coolant_flow.flux_multiplier, required in COOLANT_ACT mode
        flux_multiplier = float(config.get('coolant_flow', 'flux_multiplier'))
        if aim in ['COOLANT_ACT_PRE', 'COOLANT_ACT_POST'] and flux_multiplier is None:
            raise ValueError(
                "flux_multiplier must be provided in COOLANT_ACT mode")

    # fispact
    if aim in ('CELL_ACT_PRE', 'CELL_ACT_POST',
               'CELL_DPA_PRE', 'CELL_DPA_POST',
               'COOLANT_ACT_PRE', 'COOLANT_ACT_POST',
               'CELL_RWC_VIS', 'CELL_MAT_EVO'):
        # fispact.fispact_material_list, optional
        fispact_material_list = config.get(
            'fispact', 'fispact_material_list', fallback='')
        if fispact_material_list != '':
            fispact_material_list = os.path.join(
                work_dir, fispact_material_list)
        # fispact.irradiation_scenario, required in CELL_ACT and CELL_DPA mode
        irradiation_scenario = config.get('fispact', 'irradiation_scenario')
        if aim in ['CELL_ACT_PRE', 'CELL_ACT_POST', 'CELL_DPA_PRE', 'CELL_DPA_POST']:
            if irradiation_scenario == '':
                raise ValueError(
                    "irradiation_scenario must be provided in CELL_ACT and CELL_DPA mode")
            irradiation_scenario = utils.valid_input_file(os.path.join(
                work_dir, irradiation_scenario), irradiation_scenario)
        if aim in ['COOLANT_ACT_PRE', 'COOLANT_ACT_POST']:
            if irradiation_scenario != '':
                raise ValueError(
                    "irradiation_scenario is not required in COOLANT_ACT mode")
        # fispact.nuc_treatment, optional
        nuc_treatment = config.get('fispact', 'nuc_treatment', fallback='')
        if nuc_treatment != '':
            nuc_treatment = utils.valid_input_file(
                os.path.join(work_dir, nuc_treatment), nuc_treatment)
        # fispact.fispact_files_dir, optional
        fispact_files_dir = config.get(
            'fispact', 'fispact_files_dir', fallback='')
        if fispact_files_dir != '' and aim != 'CELL_MAT_EVO':
            fispact_files_dir = os.path.join(work_dir, fispact_files_dir)
            os.system(f'mkdir -pv {fispact_files_dir}')
        # fispact.fispact_data_dir, optional
        if aim in ['CELL_ACT_PRE', 'CELL_MAT_EVO', 'COOLANT_ACT_PRE', 'CELL_DPA_PRE']:
            fispact_data_dir = get_fispact_data_dir(filename, config)
        # fispact.dose
        if aim in ['CELL_ACT_PRE', 'CELL_ACT_POST']:
            ndose, dist = get_ndose_dist(config)
        # time_step, required only in CELL_MAT_EVO mode
        power_time_step = None
        if aim in ['CELL_MAT_EVO']:
            power_time_step = float(config.get('fispact', 'power_time_step'))

    # model, required
    part_cell_list = os.path.join(work_dir,
                                  config.get('model', 'part_cell_list'))
    # model.model_degree, optional
    model_degree = float(config.get('model', 'model_degree', fallback=360.0))
    if model_degree < 0.0 or model_degree > 360.0:
        raise ValueError('model_degree must between 0 ~ 360')

    # [radwaste] standard
    # deprecated key words check
    try:
        item = config.get('radwaste', 'radwaste_standard')
    except:
        pass
    else:
        raise ValueError(
            f"Keyword 'RADWASTE_STANDARD' is deprecated, use 'RADWASTE_STANDARDS'")
    rwss = get_radwaste_standards(config, verbose=True)

    # [debug]
    # deprecated key words check
    try:
        item = config.get('debug', 'monitor_cell')
    except:
        pass
    else:
        raise ValueError(
            f"Keyword 'MONITOR_CELL' is deprecated, use 'MONITOR_CELLS'")
    # monitor nucs

    # [photon_source]
    # output photon source information for cell-based r2s
    out_phtn_src = False
    try:
        out_phtn_src = config.getboolean('photon_source', 'out_phtn_src')
    except:
        pass

    return True


@utils.log
def get_cooling_times(irradiation_scenario, aim=None):
    """Read the irradiation_scenario, return cooling_time[]
        report error if the irradiation_scenario not fit the need of the aim (CELL_DPA).
        CELL_DPA requirement: 1. only one pulse allowed, and this must be the FULL POWER YEAR, 1 year
                              2. no cooling time allowed."""
    # check the IRRADIATiON_SCENARIO file
    errmsg = ''.join(['irradiation_scenario ERROR:\n',
                      '1. Only one pulse allowed, and it must be a FPY (1 YEARS).\n',
                      '2. No cooling time allowed.'])
    # check there is only one Pulse in the content
    if aim in ('CELL_DPA_PRE', 'CELL_DPA_POST'):
        fin = open(irradiation_scenario)
        time_count = 0
        for line in fin:
            line_ele = line.split()
            if line_ele == 0:  # end of the file
                continue
            if line[0] == '<' and line[1] == '<':  # this is a comment line
                continue
            if 'TIME' in line:  # this is the time information line
                time_count += 1
                if ' 1 ' not in line or ' YEARS ' not in line:  # error
                    raise ValueError(errmsg)
        fin.close()
        if time_count != 1:  # error
            raise ValueError(errmsg)

    cooling_time = []
    fin = open(irradiation_scenario, 'r', encoding='utf-8')
    zero_flag = False
    for line in fin:
        line_ele = line.split()
        if len(line_ele) == 0:  # this is a empty line
            continue
        if line[0] == '<' and line[1] == '<':  # this is a comment line
            continue
        if 'ZERO' in line:
            zero_flag = True
            continue
        if 'TIME' in line and zero_flag:  # this is a information about the cooling time
            cooling_time.append(
                utils.time_to_sec(float(line_ele[1]), line_ele[2]))
    fin.close()
    return cooling_time


def get_cooling_times_cul(cooling_times):
    """Calculate the cumulated cooling times."""
    cooling_times_cul = [0.0]*len(cooling_times)
    for i in range(len(cooling_times)):
        cooling_times_cul[i] = cooling_times_cul[i-1] + cooling_times[i]
    return cooling_times_cul


@utils.log
def get_fispact_materials(fispact_material_list, aim=None, verbose=True):
    """get_fispact_materials: read the fispact_material_list file to get the link of
    return the fispact_materials (of int) and fispact_materials_paths (of string)
    Where the fispact_materials contains the material id
              fispact_materials_paths contains the material file in fispact format"""

    fispact_materials = []
    fispact_materials_paths = []
    # check for the config.ini
    if fispact_material_list == '':
        fispact_materials, fispact_materials_paths = [], []
    else:
        if verbose:
            print(
                f"    the materials defined in {fispact_material_list} will be used to replace that in MCNP input")
        # read the fispact_material_list to get the information
        fin = open(fispact_material_list)
        try:
            for line in fin:
                line_ele = line.split()
                # is this line a comment line?
                if utils.is_comment(line, code='#'):
                    pass
                else:
                    material_path = line_ele[0]
                    if material_path in fispact_materials_paths:
                        errmsg = ''.join(
                            ['material path:', material_path, ' defined more than once in fispact_material_list\n'])
                        raise ValueError(errmsg)
                    else:
                        fispact_materials_paths.append(material_path)
                        if aim in ['COOLANT_ACT_PRE', 'COOLANT_ACT_POST']:
                            # part name supports explicit define only
                            fispact_materials.append(line_ele[1:])
                        else:
                            fispact_materials.append(
                                get_cell_ids(line_ele[1:]))
        except BaseException:
            errmsg = ''.join(
                ['Error produced when reading fispact_material_list'])
            print(errmsg)
    check_material_list(fispact_materials, aim=aim)
    # print the information
    if verbose:
        for i in range(len(fispact_materials_paths)):
            print(
                f"    material defined in {fispact_materials_paths[i]} will used to replace {fispact_materials[i]}")
    return fispact_materials, fispact_materials_paths


def get_cell_ids_sub(value):
    """get_cells_id_sub, used to interpret a string of cell list to int list of cell ids"""
    cell_ids_sub = []
    if '~' in value:  # this string need to expand
        cell_ele = value.split('~')
        pre_cell, post_cell = int(cell_ele[0]), int(cell_ele[-1])
        for i in range(pre_cell, post_cell + 1, 1):
            cell_ids_sub.append(i)
    else:
        cell_ids_sub.append(int(value))
    return cell_ids_sub


def get_cell_ids(value):
    """get_cell_ids, used to get cell ids from the context read from part_cell_list
    input: value, this is a list of string, that need to interpret to cell ids
    return: a list of int that represent the cell ids"""
    cell_ids = []
    for item in value:
        cell_ids_sub = get_cell_ids_sub(item)
        cell_ids.extend(cell_ids_sub)
    return cell_ids


def get_item_ids(value):
    """
    Used to get items (cells or parts or both) from nuc_treatment.
    """
    items = []
    for item in value:
        if '~' in item:  # it contains cell range
            cell_ids_sub = get_cell_ids_sub(item)
            items.extend(cell_ids_sub)
        elif is_item_cell(item):
            items.append(int(item))
        elif is_item_part(item):
            items.append(item)
    return items


@utils.log
def get_nodes(coolant_flow_parameters):
    """Get nodes, read COOLNAT_FLOW_PARAMETERS to define nodes"""
    nodes = []
    df = pd.read_csv(coolant_flow_parameters)
    cols = df.columns
    for i in range(3, len(cols), 2):
        node_name = cols[i].split('(s)')[0].strip()
        node = Part()
        node.id = node_name
        node.init_equal_cell()
        node.node_part_count = list(np.array(df[node_name + ' counts']))
        nodes.append(node)
    return nodes


@utils.log
def get_cell_need_cal(aim, parts):
    """calculate the cell need to cal according to the aim and parts
        input: aim, the aim of the run
        input: parts, the parts that need to run
        return: cell_need_cal, a list of cells that need to perform FISPACT run
        CONDITION 1: if the aim is 'CELL_DPA_PRE/POST' or the 'CELL_ACT_PRE/POST', then the parts must be given
               and then the cell_need_cal will be the cells listed in the parts."""
    # judge the condition
    cell_need_cal = []
    cids_lack_flux = []
    if aim in ('CELL_DPA_PRE', 'CELL_DPA_POST', 'CELL_ACT_PRE',
               'CELL_ACT_POST', 'CELL_MAT_EVO'):  # parts should be given
        if len(parts) == 0:
            raise ValueError(f"parts must be given when aim: {aim}")
        else:
            for p in parts:
                for c in p.part_cell_list:
                    if c not in cell_need_cal:
                        cell_need_cal.append(c)
                        if len(c.neutron_flux) == 0:
                            cids_lack_flux.append(c.id)
    if len(cids_lack_flux) > 0:
        errmsg = ''.join(
            ['cells:', str(cids_lack_flux), ' lack neutron flux information'])
        raise ValueError(errmsg)
    return cell_need_cal


def get_fispact_file_prefix(work_dir, ele_id, ele_type='c',
                            fispact_files_dir=''):
    """
    Get the fispact file prefix.
    """
    if fispact_files_dir == '':
        file_prefix = os.path.join(work_dir, f"{ele_type}{ele_id}")
    else:
        file_prefix = os.path.join(fispact_files_dir, f"{ele_type}{ele_id}")
    return file_prefix


def check_file_for_keyword(file_path, keyword, reverse=True):
    """
    Checks if a given keyword is present in a file.

    Args:
        file_path (str): The path to the file to be checked.
        keyword (str): The keyword to search for in the file.
        reverse (bool): If True, search from the end of the file. If False, search from the beginning.

    Returns:
        bool: True if the keyword is found in the file, False otherwise.
        None: If the file is not accessible due to an IOError.

    Raises:
        IOError: If the file cannot be accessed.
    """
    try:
        with open(file_path, 'rb') as f:
            if reverse:
                # Read the file in reverse
                f.seek(0, os.SEEK_END)
                file_size = f.tell()
                buffer_size = 1024
                while file_size > 0:
                    offset = min(buffer_size, file_size)
                    f.seek(-offset, os.SEEK_CUR)
                    buffer = f.read(offset).decode('utf-8')
                    if keyword in buffer:
                        return True
                    f.seek(-offset, os.SEEK_CUR)
                    file_size -= offset
            else:
                # Read the file from the beginning
                for line in f:
                    if keyword in line.decode('utf-8'):
                        return True
            return False
    except IOError:
        raise FileNotFoundError(f"ERROR: File {file_path} not accessible")


def if_fispact_output_files_accessible_and_complete(itemlist, work_dir, fispact_files_dir, content):
    """
    Checks if FISPACT output files are accessible and complete for given items.

    Args:
        itemlist (list): List of items to check, which can be instances of Cell or Part.
        work_dir (str): The working directory where the files are located.
        fispact_files_dir (str): The directory where FISPACT files are stored.
        content (list): List of content suffixes to check in the files.

    Returns:
        list: A list of file prefixes for incomplete cells.

    Raises:
        RuntimeError: If any FISPACT files are not accessible.
    """
    def get_file_prefix(item):
        if isinstance(item, Cell):
            return get_fispact_file_prefix(work_dir, ele_id=item.id, ele_type='c', fispact_files_dir=fispact_files_dir)
        elif isinstance(item, Part):
            return get_fispact_file_prefix(work_dir, ele_id=item.id, ele_type='p', fispact_files_dir=fispact_files_dir)
        return None

    incomplete_cells = []
    inaccessible_files = []

    for item in itemlist:
        file_prefix = get_file_prefix(item)
        if not file_prefix:
            continue

        for cnt in content:
            check_file_name = f"{file_prefix}{cnt}"
            result = check_file_for_keyword(
                check_file_name, 'Current time')
            if result is None:
                inaccessible_files.append(check_file_name)
            elif not result:
                incomplete_cells.append(file_prefix)

    if inaccessible_files:
        raise RuntimeError(
            f"The following FISPACT files are not accessible: {', '.join(inaccessible_files)}")

    return incomplete_cells


def create_and_clean_folder(work_dir, fispact_files_dir, incomplete_cells):
    """
        This function performs the following steps:
        1. Writes the list of incomplete cells to a file named "incomplete_tasks.txt" in the specified work directory.
        2. Removes the destination folder if it already exists.
        3. Creates a new destination folder.
        4. Copies uncomputed .i and .flx files from the source folder to the destination folder based on the list of incomplete cells.

        Args:
            work_dir (str): The working directory where the source and destination folders are located.
            fispact_files_dir (str): The name of the directory containing FISPACT files within the work directory.
            incomplete_cells (list of str): A list of cell names that are incomplete and need to be copied.

        Returns:
            None
    """

    # Define paths
    incomplete_file_path = os.path.join(
        work_dir, "incomplete_tasks.txt")
    source_folder = os.path.join(work_dir, fispact_files_dir)
    destination_folder = os.path.join(
        work_dir, f"{fispact_files_dir}_incomplete")

    # Write incomplete cells to a file
    try:
        with open(incomplete_file_path, "w") as f:
            for cell_name in incomplete_cells:
                f.write(cell_name + "\n")
    except IOError as e:
        print(f"Error writing to {incomplete_file_path}: {e}")
        return

    # Read incomplete cells into a set for faster lookup
    cell_ids = {os.path.basename(cell_name)for cell_name in incomplete_cells}

    # Remove destination folder if it exists
    if os.path.exists(destination_folder):
        try:
            shutil.rmtree(destination_folder)
        except IOError as e:
            print(f"Error removing {destination_folder}: {e}")
            return

    # Create destination folder
    try:
        os.makedirs(destination_folder)
    except IOError as e:
        print(f"Error creating {destination_folder}: {e}")
        return

    # Traverse through the source folder and copy only the uncomputed .i and .flx files
    try:
        for root, _, files in os.walk(source_folder):
            for filename in files:
                if filename.endswith('.i') or filename.endswith('.flx'):
                    cell_id = filename.split('.')[0]
                    if cell_id in cell_ids:
                        source_file_path = os.path.join(root, filename)
                        destination_file_path = os.path.join(
                            destination_folder, filename)
                        shutil.copy2(source_file_path, destination_file_path)
    except IOError as e:
        print(f"Error copying files: {e}")
        return

    print(f"Folders have been created and populated: {destination_folder}")


def check_fispact_output_files(itemlist, work_dir, aim, fispact_files_dir=''):
    """
    check_fispact_output_files, check whether all the output files needed are available and complete.
    input: itemlist, a list of cells/meshes that contains all the items needed to calculate
    work_dir, the working directory
    content, what files are checked, a tuple of '.out','.tab4'
    raise a error when some file are missing, return nothing if all the files are OK.
    """

    if aim not in ['CELL_ACT_POST', 'CELL_DPA_POST', 'COOLANT_ACT_POST', 'CELL_MAT_EVO']:
        raise RuntimeError(
            'check_fispact_output_files not support aim: {0}'.format(aim))
    if aim in ['CELL_ACT_POST', 'CELL_DPA_POST', 'COOLANT_ACT_POST', 'CELL_MAT_EVO']:
        content = ('.out',)

    incomplete_cells = if_fispact_output_files_accessible_and_complete(
        itemlist, work_dir, fispact_files_dir, content)

    if incomplete_cells:
        print("Incomplete FISPACT files:")
        for cell_name in incomplete_cells:
            print(cell_name)

        # Generate a folder that contains all the files that have not been calculated
        create_and_clean_folder(work_dir, fispact_files_dir, incomplete_cells)

        raise RuntimeError(
            f"FISPACT output incomplete, please check 'incomplete_tasks.txt' and folder 'fispact_files_incomplete' for details.")


def check_interval_list(item_list, work_dir, fispact_files_dir=''):
    """
    Check the interval lists in the different output files.
    Parameters:
    item_list: list of cells or meshes
    """
    # check the mode CELL/PART
    mode = ''
    if (len(item_list) == 0):
        raise ValueError(
            'numbers of files to check is zero, there must be error, check!')
    if isinstance(item_list[0], Cell):
        mode = 'CELL'
        cooling = True
    if isinstance(item_list[0], Part):
        mode = 'PART'
        cooling = False
    if (mode == ''):
        raise ValueError('item_list to be checked not belong to Cell or Part')

    ref_interval_list = []
    # read the interval list for each item
    for i, item in enumerate(item_list):
        if mode == 'CELL':
            file_prefix = get_fispact_file_prefix(work_dir, ele_id=item.id,
                                                  ele_type='c', fispact_files_dir=fispact_files_dir)
        if mode == 'PART':
            file_prefix = get_fispact_file_prefix(work_dir, ele_id=item.id,
                                                  ele_type='p', fispact_files_dir=fispact_files_dir)
        filename = f"{file_prefix}.out"
        if i == 0:
            ref_interval_list = get_interval_list(filename)
            ref_filename = filename
        interval_list = get_interval_list(filename)
        if interval_list != ref_interval_list:
            raise ValueError("File {0} has different interval list from the {1}".format(
                filename, ref_filename))
    # no different found, get cooling interval
    interval_list = get_interval_list(filename, cooling_only=cooling)
    return interval_list


def get_material_path(mat_chain_list, path_list, mid):
    """
    Find the material path to replace.
    """
    for i, item in enumerate(mat_chain_list):
        if mid in item:
            return path_list[i]
    raise ValueError("Material path not found")


def check_material_list(mat_chain_list, aim=None):
    """
    Check material list.
    Raise ValueError when these happens:
    - mid is not int.
    - mid is negative. (mid could be 0, enable He to replace it)
    - mid is shown in more than one sublist of mat_chain_list.
    """

    extend_list = []
    # check type
    for i, sublist in enumerate(mat_chain_list):
        for j, item in enumerate(sublist):
            if aim in ['COOLANT_ACT_PRE', 'COOLANT_ACT_POST']:
                if not isinstance(item, str):
                    raise ValueError(
                        "part name {0} has wrong type or value.".format(str(item)))
            else:
                if not isinstance(item, int) or item < 0:
                    raise ValueError(
                        "mid {0} has wrong type or value.".format(str(item)))
        extend_list.extend(sublist)

    # check repeat
    extend_set = set(extend_list)
    if len(extend_set) != len(extend_list):
        # there is duplicate in the list
        for i, item in enumerate(extend_list):
            count = extend_list.count(item)
            if count > 1:
                raise ValueError(
                    "mid {0} defined more than once.".format(str(item)))
    return True


def merge_node_parts(node, parts, node_index):
    """
    Merge the data of different parts to node according to cooling interval.
    The merged data are stored in node.equal_cell.
    """
    # get the total mass flow rate
    for i, p in enumerate(parts):
        node.mass_flow_rate += p.mass_flow_rate * node.node_part_count[i]
    # treat the nuclide and half-life
    for i, p in enumerate(parts):
        for j, nuc in enumerate(p.equal_cell.nuclides):
            if nuc in node.equal_cell.nuclides:
                pass
            else:
                # add the nuc into node
                node.equal_cell.nuclides.append(nuc)
                node.equal_cell.half_lives.append(p.equal_cell.half_lives[j])
    # treat the act, decay heat, contact_dose and ci
    NUC = len(node.equal_cell.nuclides)
    INTV = len(parts[0].equal_cell.act)
    node.equal_cell.act = np.resize(node.equal_cell.act, (1, NUC))
    node.equal_cell.total_alpha_act = np.resize(
        node.equal_cell.total_alpha_act, (INTV-1))
    node.equal_cell.decay_heat = np.resize(
        node.equal_cell.decay_heat, (1, NUC))
    node.equal_cell.contact_dose = np.resize(
        node.equal_cell.contact_dose, (1, NUC))
    node.equal_cell.ci = np.resize(node.equal_cell.ci, (1, NUC))
    node.equal_cell.gamma_emit_rate = np.resize(
        node.equal_cell.gamma_emit_rate, (1, 24))
    # merge the data
    for i, p in enumerate(parts):
        for j, nuc in enumerate(p.equal_cell.nuclides):
            nidx = node.equal_cell.nuclides.index(nuc)
            node.equal_cell.act[0][nidx] += p.equal_cell.act[node_index+1][j] * (
                p.mass_flow_rate*node.node_part_count[i]/node.mass_flow_rate)  # unit: Bq/kg
            node.equal_cell.decay_heat[0][nidx] += p.equal_cell.decay_heat[node_index+1][j] * (
                p.mass_flow_rate*node.node_part_count[i]/node.mass_flow_rate)  # kW/kg
            node.equal_cell.contact_dose[0][nidx] += p.equal_cell.contact_dose[node_index+1][j] * (
                p.mass_flow_rate*node.node_part_count[i]/node.mass_flow_rate)  # Sv/h
            node.equal_cell.ci[0][nidx] += p.equal_cell.ci[node_index+1][j] * \
                (p.mass_flow_rate*node.node_part_count[i]/node.mass_flow_rate)
        for intv in range(INTV-1):
            node.equal_cell.total_alpha_act[intv] += p.equal_cell.total_alpha_act[node_index+1] * (
                p.mass_flow_rate*node.node_part_count[i]/node.mass_flow_rate)  # kW/kg
        for eb in range(24):
            node.equal_cell.gamma_emit_rate[0][eb] += p.equal_cell.gamma_emit_rate[node_index+1][eb] * (
                p.mass_flow_rate*node.node_part_count[i]/node.mass_flow_rate)


def get_nuc_treatments_new(nuc_treatment):
    """
    Read the file nuc_treatment and get information.

    Parameters:
    -----------
    nuc_treatment: str
        The filename of nuc_treatment.

    Returns:
    --------
    nuc_trts: list
        List of the nuclide treatments.
    """

    nuc_trts = []
    if nuc_treatment == '':
        return nuc_trts
    fin = open(nuc_treatment, 'r')
    line = ' '
    while line != '':
        try:
            line = fin.readline()
        except:
            line = fin.readline().encode('ISO-8859-1')
        if utils.is_blank_line(line):  # this is a empty line
            continue
        if utils.is_comment(line, code='#'):  # this is a comment line
            continue
        nt = nuc_treat.compose_nuc_treat_from_line(line)
        nuc_trts.append(nt)
    fin.close()
    return nuc_trts


def expand_nuc_treatment_ids_new(nt, cells, parts):
    """
    Expand the item_nuc_treatments. The item_nuc_treatments contains list of Cell and Part.
    This function expand the Part into cells.
    Noting:
        - The same treatment to a cell will be combined, only perform once.
          For example, A contains cell 1 and 2. The treatment [[1, H3, 0.01], [A, H3, 0.01]]
          will be expanded to [[1, H3, 0.01], [2, H3, 0.01]]
        - Different level of extraction will be combined, only perform the one
          with lower retain. For example, [[1, H3, 0.01], [A, H3, 0.001]] will
          be expanded to [[1, H3, 0.001], [2, H3, 0.001]]

    Parameters:
    -----------
    nuc_trts : list of NucTreat objects
    """
    if len(nt.ids) == 0:
        return nt

    cell_nuc_treatments = []
    # put all pairs together
    for i, item in enumerate(nt.ids):
        if is_item_cell(item, cells):
            cell_nuc_treatments.append(item)
        elif is_item_part(item, parts):
            pidx = utils.find_index_by_property(item, parts)
            for cid in parts[pidx].cell_ids:
                cell_nuc_treatments.append(cid)
    # sort
    cell_nuc_treatments.sort()
    nt.ids = cell_nuc_treatments
    return nt


def get_tally_property(config):
    """Get the tally property"""
    try:
        tally_property = config.get('mcnp', 'tally_property').split(',')
        if len(tally_property) > 1:
            raise ValueError(
                f"Please parse only 1 kind of the tally property at once")
        else:
            tally_property = tally_property[0]
    except:
        # set default value
        tally_property = 'neutron_flux'
    return tally_property


def get_tally_unit(config):
    """Get the tally unit"""
    try:
        tally_unit = config.get('mcnp', 'tally_unit')
    except:
        # set default value
        tally_unit = 'n/cm2/s'
    return tally_unit


def get_tally_numbers(config):
    """Get the tally number from config file"""
    tally_numbers = config.get('mcnp', 'tally_numbers').split(',')
    for i, tn in enumerate(tally_numbers):
        try:
            tally_numbers[i] = int(tally_numbers[i])
        except:
            raise ValueError(f"tally_numbers must be integer")
    for tn in tally_numbers:
        if tn < 0 or (tn % 10) != 4:
            raise ValueError(
                f'Wrong tally_numbers {tn}, must great than 0 and ended with 4')
    return tally_numbers


def get_nuclide_sets(config):
    """Get the nuclide sets from config file"""
    tokens = config.get('mcnp', 'nuclide_sets',
                        fallback='FENDL3, TENDL2019').split(',')
    nuclide_sets = []
    for i, item in enumerate(tokens):
        nuc_set = tokens[i].strip().upper()
        if nuc_set not in SUPPORTED_NUC_SETS:
            raise ValueError(f"{tokens[i]} not a supported nuclide set")
        nuclide_sets.append(tokens[i].strip())
    return nuclide_sets


def get_wwinp(config):
    item = None
    try:
        item = config.get('mcnp', 'wwinp')
    except:
        pass
    if item:
        print(f"    The {item} will be used as weight window")
        return item
    else:
        return None


def get_monitor_cells(config):
    """Get the cells to monitor the behavior vs. iterations"""
    tokens = config.get('debug', 'monitor_cells').split(',')
    cids = []
    for item in tokens:
        item = item.strip()
        try:
            cid = int(item)
            if cid not in cids:
                cids.append(cid)
            else:
                print(f"    WARNING: monitor cell {cid} repeated!")
        except:
            raise ValueError(f"MONITOR_CELL encountered wrong input: {item}")
    return cids


def get_monitor_nucs(config):
    """Get the nuclides to monitor the behavior vs. iterations"""
    tokens = config.get('debug', 'monitor_nucs').split(',')
    nucs = []
    for item in tokens:
        item = item.strip()
        if item not in nucs:
            nucs.append(item)
        else:
            print(f"    WARNING: monitor nuc: {nucs} repeated!")
    return nucs


def get_radwaste_standards(config, verbose=False):
    """Get the radwaste standards from config file."""

    tokens = config.get('radwaste', 'radwaste_standards',
                        fallback='').split(',')
    radwaste_standards = []
    for item in tokens:
        item = item.strip()
        if item == '':
            continue
        if item.upper() not in SUPPORTED_RADWASTE_STANDARDS:
            raise ValueError(f"Radwaste standard {item} not supported!")
        radwaste_standards.append(item)

    if verbose:
        if len(radwaste_standards) == 0:
            print("    WARNING: no radwaste standards used")
        else:
            print("    radwaste standards used to classify radwaste:",
                  radwaste_standards)
    # construct RadwasteStandard objects
    rwss = []
    for item in radwaste_standards:
        match item.strip():
            case 'CHN2018':
                rws = RadwasteStandardChina(item.strip())
            case 'UK':
                rws = RadwasteStandardUK(item.strip())
            case 'USNRC':
                rws = RadwasteStandardUS(item.strip())
            case 'USNRC_FETTER':
                rws = RadwasteStandardUS(item.strip())
            case 'RUSSIAN':
                rws = RadwasteStandardRussia(item.strip())
            case 'FRANCE':
                rws = RadwasteStandardFrance(item.strip())
            case _:
                raise TypeError('you need to specify the exact standard')
        rwss.append(rws)

    return rwss


def get_fispact_data_dir(filename, config=None, verbose=True):
    if config is None:
        config = configparser.ConfigParser()
        config.read(filename)
    work_dir = get_work_dir(filename, config=config)
    fispact_data_dir_ori = config.get(
        'fispact', 'fispact_data_dir', fallback='')
    if fispact_data_dir_ori == '':
        return fispact_data_dir_ori

    # treat rel/abs path
    if verbose:
        print(f"    warning: FISPACT run can be automatically performed for NATF >= 1.9.4 if FISPACT_DATA_DIR is provided")
    if '$HOME' in fispact_data_dir_ori:
        fispact_data_dir = fispact_data_dir_ori.replace('$HOME', '~')
    if '~' in fispact_data_dir_ori:
        fispact_data_dir = os.path.expanduser(fispact_data_dir_ori)
    fispact_data_dir = utils.valid_input_dir(os.path.join(
        work_dir, fispact_data_dir_ori), fispact_data_dir_ori)
    return fispact_data_dir


def read_mat_evo_status(filename):
    """
    Check the workflow status of CELL_MAT_EVO.
    Information in the status file:
        - TOTAL_STEPS:
        - CURRENT_STEP:
        - STAT:

    Parameters:
    -----------
    status_file: str
        The status file. Default: status.ini

    Returns:
    --------
    total_steps: int
        Total steps of the workflow.
    current_step: int
        The step index
    stat: str
        The status of the current step, could be 'PRE' or 'POST'.
    """

    status = configparser.ConfigParser()
    status.read(filename)
    total_steps = int(status.get('status', 'TOTAL_STEPS'))
    current_step = int(status.get('status', 'CURRENT_STEP'))
    stat = status.get('status', 'STAT')
    return total_steps, current_step, stat


def update_mat_evo_status(filename, total_steps, current_step, stat):
    """
    Check the workflow status of CELL_MAT_EVO.
    Information in the status file:
        - TOTAL_STEPS:
        - CURRENT_STEP:
        - STAT:
    """
    with open(filename, 'w') as fo:
        fo.write(f"[status]\n")
        fo.write(f"TOTAL_STEPS: {total_steps}\n")
        fo.write(f"CURRENT_STEP: {current_step}\n")
        fo.write(f"STAT: {stat}\n")


def update_tbr_file(filename, operation_time, tbr):
    """
    Update the TBR for current step.
    """
    with open(filename, 'a') as fo:
        fo.write(
            f"{utils.fso(operation_time)},{utils.fso(tbr)}\n")


def get_irr_and_cooling_times(part_name, coolant_flow_parameters):
    """
    Get irradiation time and cooling times according to part name and
    coolant flow parameters.
    """
    df = pd.read_csv(coolant_flow_parameters)
    cols = df.columns
    part_info = np.array(df.loc[df['Parts'] == part_name], dtype=str).flatten()
    irr_time = float(part_info[2])
    cooling_times_s = []
    for i in range(3, len(cols), 2):
        cooling_times_s.append(part_info[i])
    cooling_times = [float(x) for x in cooling_times_s]
    return irr_time, cooling_times


def read_file_reverse(file_path):
    """
    Reads a file line by line from the end to the start.

    Args:
        file_path (str): The path to the file to be read.

    Yields:
        str: The next line from the end of the file.
    """
    with open(file_path, 'rb') as f:
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
        buffer_size = 1024
        buffer = b''
        while file_size > 0:
            offset = min(buffer_size, file_size)
            f.seek(-offset, os.SEEK_CUR)
            buffer = f.read(offset) + buffer
            f.seek(-offset, os.SEEK_CUR)
            file_size -= offset
            while b'\n' in buffer:
                line, buffer = buffer.rsplit(b'\n', 1)
                yield line.decode('utf-8')
        if buffer:
            yield buffer.decode('utf-8')
