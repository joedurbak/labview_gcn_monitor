import gcn_custom as gcn
import settings
import os
from xmltodict import parse, unparse
from six.moves.urllib.parse import quote_plus
import collections
from astropy.coordinates import EarthLocation, SkyCoord
from astropy.time import Time
from astropy.coordinates import AltAz
import pickle
from astroplan import Observer, FixedTarget
from datetime import timezone

notice_types = settings.EXCLUDED_NOTICE_TYPES
archived_xml_dir = settings.ARCHIVED_XML_DIR
output_html_dir = settings.OUTPUT_HTML_DIR
template_html_dir = settings.TEMPLATE_HTML_DIR

html_templates_dict = settings.HTML_TEMPLATES_DICT


def dct_loc():
    try:
        return pickle.load(open(settings.DCT_LOC_PICKLE, 'rb'))
    except FileNotFoundError:
        dct_loc_obj = EarthLocation.of_site('Discovery Channel Telescope')
        file = open(settings.DCT_LOC_PICKLE, 'wb')
        pickle.dump(dct_loc_obj, file)
        file.close()
        return dct_loc_obj


def dct_astroplan_loc():
    try:
        return pickle.load(open(settings.DCT_ASTROPLAN_LOC_PICKLE, 'rb'))
    except FileNotFoundError:
        dct_loc_obj = Observer.at_site('Discovery Channel Telescope')
        file = open(settings.DCT_ASTROPLAN_LOC_PICKLE, 'wb')
        pickle.dump(dct_loc_obj, file)
        file.close()
        return dct_loc_obj


def is_blank_dict(test_dict):
    for value in test_dict.values():
        if value != "":
            return False
    return True


def filename_cleaner(filename):
    filename_split = filename.split('%2F')
    return filename_split[len(filename_split) - 1]


def format_html(string, input_dict):
    if is_blank_dict(input_dict):
        return ""
    for key, value in input_dict.items():
        string = string.replace(r"{" + str(key) + r"}", str(value))
    return string


def xml_tag_loader(xml_dictionary, key_tuple):
    try:
        value = xml_dictionary.copy()
    except AttributeError:
        value = xml_dictionary
    for key in key_tuple:
        try:
            value = value[key]
        except KeyError:
            return ""
        except TypeError:
            if type(value) is list:
                try:
                    value = value[0][key]
                except KeyError or TypeError:
                    return ""
            else:
                return ""
    return value


def radec_to_altaz(
        ra, dec, time_iso_str, unit,
        observing_location=dct_loc(),
):
    observing_time = Time(time_iso_str)
    aa = AltAz(location=observing_location, obstime=observing_time)
    coord = SkyCoord(ra, dec, unit=unit)
    altaz_coord = coord.transform_to(aa)
    alt = altaz_coord.alt.degree
    az = altaz_coord.az.degree
    return alt, az


def format_decimal_places(number, decimal_places):
    integers, decimals = str(number).split('.')
    current_dec_place = len(decimals)
    if current_dec_place > decimal_places:
        decimals = decimals[0:decimal_places]
    else:
        for i in range(decimal_places-current_dec_place):
            decimals += '0'
    return '.'.join((integers, decimals))


def count_decimal_places(number):
    try:
        decimals = str(number).split('.')[1]
        return len(decimals)
    except IndexError:
        return 0


def list_plus(possible_list):
    if (type(possible_list) is not list) and (type(possible_list) is not tuple):
        if isinstance(possible_list, collections.Mapping):
            return [possible_list]
        else:
            return []
    return possible_list


class GRBVisibilityAtDCT:
    def __init__(self, ra, dec, unit, utc_time):
        self.coord = SkyCoord(ra, dec, unit=unit)
        self.time = Time(utc_time)
        self.dct = dct_astroplan_loc()
        self.grb = FixedTarget(name='GRB', coord=self.coord)
        self.target_is_up = self.dct.target_is_up(self.time.now(), self.grb)
        self.target_rise_time = self.dct.target_rise_time(self.time.now(), self.grb)
        self.target_set_time = self.dct.target_set_time(self.time.now(), self.grb)
        self.target_rise_time_local = self.target_rise_time.datetime.replace(tzinfo=timezone.utc).astimezone(tz=None)


class HTMLOutput:
    def __init__(
            self, xml_payload,
            voevent_html, who_html, what_html, wherewhen_html, how_html, why_html, citations_html, citation_html,
            reference_html, references_html, authors_html, author_html, param_html, params_html,
            table_html, tables_html, field_html, fields_html, observation_location_html, observatory_location_html,
            astro_coords_html, time_instant_html, position2d_html, position3d_html, inferences_html,
            inference_html, event_ivorn_html, event_ivorns_html, icon_html, modal_html, group_html, groups_html,
            container_html, simple_row_html
    ):
        self.xml_dict = parse(xml_payload)['voe:VOEvent']
        self.voevent_html = open(voevent_html, 'r').read()
        self.who_html = open(who_html, 'r').read()
        self.what_html = open(what_html, 'r').read()
        self.wherewhen_html = open(wherewhen_html, 'r').read()
        self.how_html = open(how_html, 'r').read()
        self.why_html = open(why_html, 'r').read()
        self.citations_html = open(citations_html, 'r').read()
        self.citation_html = open(citation_html, 'r').read()
        self.reference_html = open(reference_html, 'r').read()
        self.references_html = open(references_html, 'r').read()
        self.authors_html = open(authors_html, 'r').read()
        self.author_html = open(author_html, 'r').read()
        self.param_html = open(param_html, 'r').read()
        self.params_html = open(params_html, 'r').read()
        self.table_html = open(table_html, 'r').read()
        self.tables_html = open(tables_html, 'r').read()
        self.fields_html = open(fields_html, 'r').read()
        self.field_html = open(field_html, 'r').read()
        self.observation_location_html = open(observation_location_html, 'r').read()
        self.observatory_location_html = open(observatory_location_html, 'r').read()
        self.astro_coords_html = open(astro_coords_html, 'r').read()
        self.position2d_html = open(position2d_html, 'r').read()
        self.position3d_html = open(position3d_html, 'r').read()
        self.time_instant_html = open(time_instant_html, 'r').read()
        self.inferences_html = open(inferences_html, 'r').read()
        self.inference_html = open(inference_html, 'r').read()
        self.event_ivorn_html = open(event_ivorn_html, 'r').read()
        self.event_ivorns_html = open(event_ivorns_html, 'r').read()
        self.icon_html = open(icon_html, 'r').read()
        self.modal_html = open(modal_html, 'r').read()
        self.group_html = open(group_html, 'r').read()
        self.groups_html = open(groups_html, 'r').read()
        self.container_html = open(container_html, 'r').read()
        self.simple_row_html = open(simple_row_html, 'r').read()

    def container_xml_to_html(self):
        iso_time = xml_tag_loader(self.xml_dict, (
                'WhereWhen', 'ObsDataLocation', 'ObservationLocation', 'AstroCoords', 'Time', 'TimeInstant', 'ISOTime'
            ))
        context = {
            'VOEvent': self.voevent_xml_to_html(),
            'What_Description': xml_tag_loader(self.xml_dict, ('What', 'Description')),
            'Who_Date': xml_tag_loader(self.xml_dict, ('Who', 'Date')),
            'WhereWhen_ObservationLocation_AstroCoords_Position2D_unit': xml_tag_loader(self.xml_dict, (
                'WhereWhen', 'ObsDataLocation', 'ObservationLocation', 'AstroCoords', 'Position2D', '@unit'
            )),
            'WhereWhen_ObservationLocation_AstroCoords_Position2D_Name1': xml_tag_loader(self.xml_dict, (
                'WhereWhen', 'ObsDataLocation', 'ObservationLocation', 'AstroCoords', 'Position2D', 'Name1'
            )),
            'WhereWhen_ObservationLocation_AstroCoords_Position2D_Name2': xml_tag_loader(self.xml_dict, (
                'WhereWhen', 'ObsDataLocation', 'ObservationLocation', 'AstroCoords', 'Position2D', 'Name2'
            )),
            'WhereWhen_ObservationLocation_AstroCoords_Position2D_Value2_C1': xml_tag_loader(self.xml_dict, (
                'WhereWhen', 'ObsDataLocation', 'ObservationLocation', 'AstroCoords', 'Position2D', 'Value2', 'C1'
            )),
            'WhereWhen_ObservationLocation_AstroCoords_Position2D_Value2_C2': xml_tag_loader(self.xml_dict, (
                'WhereWhen', 'ObsDataLocation', 'ObservationLocation', 'AstroCoords', 'Position2D', 'Value2', 'C2'
            )),
            'WhereWhen_ObservationLocation_AstroCoords_coord_system_id': xml_tag_loader(self.xml_dict, (
                'WhereWhen', 'ObsDataLocation', 'ObservationLocation', 'AstroCoords', '@coord_system_id'
            )),
            'ALT': '',
            'AZ': '',
            'VisibilityTime': '',
        }
        if context['WhereWhen_ObservationLocation_AstroCoords_Position2D_Name1'].lower() == 'ra':
            ra = context['WhereWhen_ObservationLocation_AstroCoords_Position2D_Value2_C1']
            dec = context['WhereWhen_ObservationLocation_AstroCoords_Position2D_Value2_C2']
        elif context['WhereWhen_ObservationLocation_AstroCoords_Position2D_Name2'].lower() == 'ra':
            ra = context['WhereWhen_ObservationLocation_AstroCoords_Position2D_Value2_C2']
            dec = context['WhereWhen_ObservationLocation_AstroCoords_Position2D_Value2_C1']
        else:
            return format_html(self.container_html, context)
        alt, az = radec_to_altaz(
            ra, dec, iso_time, context['WhereWhen_ObservationLocation_AstroCoords_Position2D_unit']
        )
        dec_places = count_decimal_places(ra)
        alt = format_decimal_places(alt, dec_places)
        az = format_decimal_places(az, dec_places)
        context['ALT'], context['AZ'] = (alt, az)
        return format_html(self.container_html, context)

    def simple_row_xml_to_html(self, left_col_str, right_col_str):
        if right_col_str == '':
            return ''
        return format_html(self.simple_row_html, {'LeftColStr': left_col_str, 'RightColStr': right_col_str})

    def voevent_xml_to_html(self):
        context = {
            "Who": self.who_xml_to_html(xml_tag_loader(self.xml_dict, ('Who', ))),
            "What": self.what_xml_to_html(xml_tag_loader(self.xml_dict, ('What', ))),
            "WhereWhen": self.wherewhen_xml_to_html(xml_tag_loader(self.xml_dict, ('WhereWhen', ))),
            "How": self.how_xml_to_html(xml_tag_loader(self.xml_dict, ('How', ))),
            "Why": self.why_xml_to_html(xml_tag_loader(self.xml_dict, ('Why', ))),
            "Citations": self.citations_xml_to_html(xml_tag_loader(self.xml_dict, ('Citations', ))),
            "Reference": self.references_xml_to_html(xml_tag_loader(self.xml_dict, ('Reference',))),
            "Description": xml_tag_loader(self.xml_dict, ('Description', )),
            "role": xml_tag_loader(self.xml_dict, ('@role', )),
            "ivorn": xml_tag_loader(self.xml_dict, ('@ivorn', )),
            'version': xml_tag_loader(self.xml_dict, ('@version', )),
        }
        return format_html(self.voevent_html, context)

    def who_xml_to_html(self, who_dict):
        context = {
            'AuthorIVORN': xml_tag_loader(who_dict, ('AuthorIVORN', )),
            'Date': xml_tag_loader(who_dict, ('Date', )),
            "Description": xml_tag_loader(who_dict, ('Description', )),
            "Reference": self.references_xml_to_html(xml_tag_loader(who_dict, ('Reference',))),
            "Authors": self.authors_xml_to_html(xml_tag_loader(who_dict, ('Author', ))),
        }
        pass
        context['DescriptionIcon'], context['DescriptionModal'] = self.icon_modal_html(
            context['Description'], 'whoModalDescription', 'description'
        )
        context['ReferenceIcon'], context['ReferenceModal'] = self.icon_modal_html(
            context['Reference'], 'whoModalDescription', 'description'
        )
        return format_html(self.who_html, context)

    def authors_xml_to_html(self, authors_list):
        markup = ""
        for author in list_plus(authors_list):
            context = {
                "title": xml_tag_loader(author, ('title', )),
                "shortName": xml_tag_loader(author, ('shortName',)),
                "contactName": xml_tag_loader(author, ('contactName',)),
                "contactEmail": xml_tag_loader(author, ('contactEmail',)),
                "contactPhone": xml_tag_loader(author, ('contactPhone',)),
                "contributor": xml_tag_loader(author, ('contributor',)),
            }
            markup += format_html(self.author_html, context)
        if markup == "":
            return markup
        context = {
            "Authors": markup,
        }
        return format_html(self.authors_html, context)

    def what_xml_to_html(self, what_dict):
        context = {
            'Params': self.params_xml_to_html(xml_tag_loader(what_dict, ('Param', ))),
            'Groups': self.groups_xml_to_html(xml_tag_loader(what_dict, ('Group', ))),
            'Tables': self.tables_xml_to_html(xml_tag_loader(what_dict, ('Table', ))),
            'Description': xml_tag_loader(what_dict, ('Description', )),
            'Reference': self.references_xml_to_html(xml_tag_loader(what_dict, ('Reference',))),
        }
        pass
        context['DescriptionIcon'], context['DescriptionModal'] = self.icon_modal_html(
            context['Description'], 'whatModalDescription', 'description'
        )
        context['ReferenceIcon'], context['ReferenceModal'] = self.icon_modal_html(
            context['Reference'], 'whatModalDescription', 'description'
        )
        return format_html(self.what_html, context)

    def params_xml_to_html(self, params_list, param_modal_id_prefix=""):
        markup = ""
        modals = ""
        params_list = list_plus(params_list)
        for param_index in range(len(params_list)):
            param = params_list[param_index]
            context = {
                "name": xml_tag_loader(param, ('@name', )),
                "value": xml_tag_loader(param, ('@value',)),
                "unit": xml_tag_loader(param, ('@unit',)),
                "ucd": xml_tag_loader(param, ('@ucd',)),
                'Description': xml_tag_loader(param, ('Description', )),
                'Reference': self.references_xml_to_html(xml_tag_loader(param, ('Reference',))),
            }
            pass
            context['DescriptionIcon'], context['DescriptionModal'] = self.icon_modal_html(
                context['Description'], '{0}ParamModalDescription{1}'.format(param_modal_id_prefix, param_index),
                'description'
            )
            context['ReferenceIcon'], context['ReferenceModal'] = self.icon_modal_html(
                context['Reference'], '{0}ParamModalReferences{1}'.format(param_modal_id_prefix, param_index),
                'references'
            )
            markup += format_html(self.param_html, context)
            modals = modals + context['ReferenceModal'] + context['DescriptionModal']
        if markup == "":
            return markup
        context = {
            "Params": markup,
            "Modals": modals,
        }
        return format_html(self.params_html, context)

    def groups_xml_to_html(self, groups_list):
        markup = ""
        groups_list = list_plus(groups_list)
        for group_index in range(len(groups_list)):
            group = groups_list[group_index]
            context = {
                "name": xml_tag_loader(group, ('@name', )),
                "type": xml_tag_loader(group, ('@type',)),
                "Params": self.params_xml_to_html(xml_tag_loader(group, ('Param', )), "Group{0}".format(group_index)),
                'Description': xml_tag_loader(group, ('Description',)),
                'Reference': self.references_xml_to_html(xml_tag_loader(group, ('Reference',))),
            }
            pass
            context['DescriptionIcon'], context['DescriptionModal'] = self.icon_modal_html(
                context['Description'], 'GroupModalDescription{0}'.format(group_index),
                'description'
            )
            context['ReferenceIcon'], context['ReferenceModal'] = self.icon_modal_html(
                context['Reference'], 'GroupModalReferences{0}'.format(group_index),
                'references'
            )
            markup += format_html(self.group_html, context)
        if markup == "":
            return markup
        context = {
            "Groups": markup,
        }
        return format_html(self.groups_html, context)

    def tables_xml_to_html(self, tables_list,):
        markup = ""
        tables_list = list_plus(tables_list)
        for table_index in range(len(tables_list)):
            table = tables_list[table_index]
            context = {
                "Fields": self.fields_xml_to_html(xml_tag_loader(table, ('Field', )), "Table{0}".format(table_index)),
                "Data": unparse(xml_tag_loader(table, ('Data',))),
                "Params": self.params_xml_to_html(xml_tag_loader(table, ('Param', )), "Table{0}".format(table_index)),
                'Description': xml_tag_loader(table, ('Description',)),
                'Reference': self.references_xml_to_html(xml_tag_loader(table, ('Reference',))),
                "name": xml_tag_loader(table, ('@name',)),
                "type": xml_tag_loader(table, ('@type',)),
            }
            pass
            context['DescriptionIcon'], context['DescriptionModal'] = self.icon_modal_html(
                context['Description'], 'TableModalDescription{0}'.format(table_index),
                'description'
            )
            context['ReferenceIcon'], context['ReferenceModal'] = self.icon_modal_html(
                context['Reference'], 'TableModalReferences{0}'.format(table_index),
                'references'
            )
            context['FieldsModals'] = context['Fields'][1]
            context['Fields'] = context['Fields'][0]
            markup += format_html(self.table_html, context)
        if markup == "":
            return markup
        context = {
            "Tables": markup,
        }
        return format_html(self.tables_html, context)

    def fields_xml_to_html(self, fields_list, field_modal_id_prefix=""):
        markup = ""
        modals = ""
        fields_list = list_plus(fields_list)
        for field_index in range(len(fields_list)):
            field = fields_list[field_index]
            context = {
                'Description': xml_tag_loader(field, ('Description',)),
                'Reference': self.references_xml_to_html(xml_tag_loader(field, ('Reference',))),
                "name": xml_tag_loader(field, ('@name',)),
                "unit": xml_tag_loader(field, ('@unit',)),
                "ucd": xml_tag_loader(field, ('@ucd',)),
            }
            pass
            context['DescriptionIcon'], context['DescriptionModal'] = self.icon_modal_html(
                context['Description'], '{0}FieldModalDescription{1}'.format(field_modal_id_prefix, field_index),
                'description'
            )
            context['ReferenceIcon'], context['ReferenceModal'] = self.icon_modal_html(
                context['Reference'], '{0}FieldModalReferences{1}'.format(field_modal_id_prefix, field_index),
                'references'
            )
            markup += format_html(self.field_html, context)
            modals = modals + context['ReferenceModal'] + context['DescriptionModal']
        if markup == "":
            return markup
        context = {
            "Fields": markup,
        }
        return format_html(self.fields_html, context), modals

    def wherewhen_xml_to_html(self, wherewhen_dict):
        context = {
            'ObservatoryLocation': self.observatory_location_xml_to_html(
                xml_tag_loader(wherewhen_dict, ('ObsDataLocation', 'ObservatoryLocation'))
            ),
            'ObservationLocation': self.observation_location_xml_to_html(
                xml_tag_loader(wherewhen_dict, ('ObsDataLocation', 'ObservationLocation'))
            ),
            'Description': xml_tag_loader(wherewhen_dict, ('Description',)),
            'Reference': self.references_xml_to_html(xml_tag_loader(wherewhen_dict, ('Reference',))),
        }
        pass
        context['DescriptionIcon'], context['DescriptionModal'] = self.icon_modal_html(
            context['Description'], 'WhereWhenModalDescription',
            'description'
        )
        context['ReferenceIcon'], context['ReferenceModal'] = self.icon_modal_html(
            context['Reference'], 'WhereWhenModalReferences',
            'references'
        )
        return format_html(self.wherewhen_html, context)

    def observatory_location_xml_to_html(self, observatory_location_dict):
        context = {
            'AstroCoordSystem': xml_tag_loader(observatory_location_dict, ('AstroCoordSystem', '@id')),
            'AstroCoords': self.astro_coords_xml_to_html(
                xml_tag_loader(observatory_location_dict, ('AstroCoords',))
            ),
        }
        return format_html(self.observatory_location_html, context)

    def observation_location_xml_to_html(self, observation_location_dict):
        context = {
            'AstroCoordSystem': xml_tag_loader(observation_location_dict, ('AstroCoordSystem', '@id')),
            'AstroCoords': self.astro_coords_xml_to_html(
                xml_tag_loader(observation_location_dict, ('AstroCoords',))
            ),
        }
        return format_html(self.observation_location_html, context)

    def astro_coords_xml_to_html(self, astro_coords_dict):
        context = {
            'Time_TimeInstant': self.simple_row_xml_to_html('Time Instant', self.time_instant_xml_to_html(
                xml_tag_loader(astro_coords_dict, ('Time', 'TimeInstant')))
            ),
            'Time_Error': self.simple_row_xml_to_html(
                'Time Error', xml_tag_loader(astro_coords_dict, ('Time', 'Error'))
            ),
            'Time_unit': self.simple_row_xml_to_html('Time Unit', xml_tag_loader(astro_coords_dict, ('Time', '@unit'))),
            'Position2D': self.simple_row_xml_to_html(
                'Position 2D', self.position2d_xml_to_html(xml_tag_loader(astro_coords_dict, ('Position2D', )))
            ),
            'Position3D': self.simple_row_xml_to_html(
                'Position 3D', self.position3d_xml_to_html(xml_tag_loader(astro_coords_dict, ('Position3D', )))
            ),
            'coord_system_id': self.simple_row_xml_to_html(
                'Coordinate System ID', xml_tag_loader(astro_coords_dict, ('@coord_system_id', ))
            ),
        }
        return format_html(self.astro_coords_html, context)

    def time_instant_xml_to_html(self, time_instant_dict):
        context = {
            'ISOTime': xml_tag_loader(time_instant_dict, ('ISOTime', )),
            'TimeScale': xml_tag_loader(time_instant_dict, ('ISOTime',)),
            'TimeOffset': xml_tag_loader(time_instant_dict, ('TimeOffset',)),
        }
        return format_html(self.time_instant_html, context)

    def position2d_xml_to_html(self, position2d_dict):
        context = {
            'Name1': xml_tag_loader(position2d_dict, ('Name1', )),
            'Name2': xml_tag_loader(position2d_dict, ('Name2',)),
            'Value2_C1': xml_tag_loader(position2d_dict, ('Value2', 'C1')),
            'Value2_C2': xml_tag_loader(position2d_dict, ('Value2', 'C2')),
            'Error2Radius': xml_tag_loader(position2d_dict, ('Error2Radius', )),
            'unit': xml_tag_loader(position2d_dict, ('@unit',)),
        }
        return format_html(self.position2d_html, context)

    def position3d_xml_to_html(self, position3d_dict):
        context = {
            'Name1': xml_tag_loader(position3d_dict, ('Name1', )),
            'Name2': xml_tag_loader(position3d_dict, ('Name2',)),
            'Name3': xml_tag_loader(position3d_dict, ('Name3',)),
            'Value3_C1': xml_tag_loader(position3d_dict, ('Value2', 'C1')),
            'Value3_C2': xml_tag_loader(position3d_dict, ('Value2', 'C2')),
            'Value3_C3': xml_tag_loader(position3d_dict, ('Value2', 'C3')),
            'unit': xml_tag_loader(position3d_dict, ('@unit',))
        }
        return format_html(self.position3d_html, context)

    def how_xml_to_html(self, how_dict):
        context = {
            'Description': xml_tag_loader(how_dict, ('Description',)),
            'Reference': self.references_xml_to_html(xml_tag_loader(how_dict, ('Reference',))),
        }
        return format_html(self.how_html, context)

    def why_xml_to_html(self, why_dict):
        context = {
            'Description': xml_tag_loader(why_dict, ('Description',)),
            'Reference': self.references_xml_to_html(xml_tag_loader(why_dict, ('Reference',))),
            'Name': self.simple_row_xml_to_html('Name', xml_tag_loader(why_dict, ('Name',))),
            'Concept': self.simple_row_xml_to_html('Concept', xml_tag_loader(why_dict, ('Concept',))),
            'Inferences': self.inferences_xml_to_html(xml_tag_loader(why_dict, ('Inference',))),
            'importance': self.simple_row_xml_to_html('Importance', xml_tag_loader(why_dict, ('@importance',))),
            'expires': self.simple_row_xml_to_html('Expires', xml_tag_loader(why_dict, ('@expires',))),
        }
        pass
        context['DescriptionIcon'], context['DescriptionModal'] = self.icon_modal_html(
            context['Description'], 'whyModalDescription', 'description'
        )
        context['ReferenceIcon'], context['ReferenceModal'] = self.icon_modal_html(
            context['Reference'], 'whyModalDescription', 'description'
        )
        return format_html(self.why_html, context)

    def inferences_xml_to_html(self, inferences_list):
        markup = ""
        inferences_list = list_plus(inferences_list)
        for inference_index in range(len(inferences_list)):
            inference = inferences_list[inference_index]
            context = {
                'Description': xml_tag_loader(inference, ('Description',)),
                'Reference': self.references_xml_to_html(xml_tag_loader(inference, ('Reference',))),
                'Name': self.simple_row_xml_to_html('Name', xml_tag_loader(inference, ('Name',))),
                'Concept': self.simple_row_xml_to_html('Concept', xml_tag_loader(inference, ('Concept',))),
                'probability': self.simple_row_xml_to_html('Probability', xml_tag_loader(inference, ('@probability',))),
                'relation': self.simple_row_xml_to_html('Relation', xml_tag_loader(inference, ('@relation',))),
            }
            pass
            context['DescriptionIcon'], context['DescriptionModal'] = self.icon_modal_html(
                context['Description'], 'InferenceModalDescription{0}'.format(inference_index),
                'description'
            )
            context['ReferenceIcon'], context['ReferenceModal'] = self.icon_modal_html(
                context['Reference'], 'InferenceModalReferences{0}'.format(inference_index),
                'references'
            )
            markup += format_html(self.inference_html, context)
        if markup == "":
            return markup
        context = {
            "Inferences": markup,
        }
        return format_html(self.inferences_html, context)

    def citations_xml_to_html(self, citations_list):
        markup = ""
        for citation in list_plus(citations_list):
            context = {
                'Description': xml_tag_loader(citation, ('Description',)),
                'EventIVORNs': self.event_ivorns_xml_to_html(xml_tag_loader(citation, ('EventIVORN',))),
            }
            markup += format_html(self.citation_html, context)
        if markup == "":
            return markup
        context = {
            "Citations": markup,
        }
        return format_html(self.citations_html, context)

    def event_ivorns_xml_to_html(self, event_ivorns_list):
        markup = ""
        for event_ivorn in list_plus(event_ivorns_list):
            context = {
                'text': xml_tag_loader(event_ivorn, ('#text',)),
                'cite': xml_tag_loader(event_ivorn, ('@cite',)),
            }
            markup += format_html(self.event_ivorn_html, context)
        if markup == "":
            return markup
        context = {
            "Events": markup,
        }
        return format_html(self.event_ivorns_html, context)

    def references_xml_to_html(self, references_list):
        markup = ""
        for reference in list_plus(references_list):
            context = {
                'type': xml_tag_loader(reference, ('@type',)),
                'uri': xml_tag_loader(reference, ('@uri',)),
            }
            markup += format_html(self.reference_html, context)
        if markup == "":
            return markup
        context = {
            "References": markup,
        }
        return format_html(self.references_html, context)

    def icon_modal_html(self, modal_message, modal_id_str, icon_type):
        if modal_message == "":
            return "", ""
        if icon_type == 'description':
            icon_class = "glyphicon glyphicon-info-sign"
            modal_header = 'Description'
        else:
            icon_class = "glyphicon glyphicon-asterisk"
            modal_header = 'References'
        icon_context = {
            'ModalID': modal_id_str,
            'SpanClass': icon_class,
        }
        modal_context = {
            'Message': modal_message,
            'Header': modal_header,
            'ModalID': modal_id_str,
        }
        return format_html(self.icon_html, icon_context), format_html(self.modal_html, modal_context)


class GCNProcessor:
    def __init__(self, incoming_xml, archive_dir, output_dir, template_dir, html_templates_dictionary, root):
        self.incoming_xml = incoming_xml
        self.archived_xml_dir = archive_dir
        self.output_html_dir = output_dir
        self.template_html_dir = template_dir
        self.html_templates_dict = html_templates_dictionary
        self.root = root

    def archive_xml(self):
        ivorn = self.root.attrib['ivorn']
        split_ivorn = ivorn.split('/')
        ivorn = split_ivorn[len(split_ivorn) - 1]
        filename = quote_plus(ivorn) + '.xml'
        file_location = os.path.join(self.archived_xml_dir, filename)
        with open(file_location, 'w') as f:
            f.write(self.incoming_xml)
            f.close()
        return file_location

    def save_output_html(self, html_string, incoming_xml_loc):
        split_path = os.path.split(incoming_xml_loc)
        file = split_path[len(split_path)-1].replace('.xml', '.html')
        output_loc = os.path.join(self.output_html_dir, file)
        output = open(output_loc, 'w')
        output.write(html_string)
        output.close()

    def gcn_processor(self):
        xml_file = self.archive_xml()
        html_handler = HTMLOutput(self.incoming_xml, **self.html_templates_dict)
        self.save_output_html(html_handler.container_xml_to_html(), xml_file)


@gcn.exclude_notice_types(*notice_types)
def handler(payload, root):
    print("{0}".format(root.attrib['ivorn']))
    incoming_xml = str(payload).lstrip('b').strip("'")
    split_xml = incoming_xml.split(r'\n')
    xml = ''
    for line in split_xml:
        xml += line.replace("\\", "")
    parsed_xml = parse(xml)
    xml = unparse(parsed_xml)
    gcn_handler = GCNProcessor(
        xml, archived_xml_dir, output_html_dir, template_html_dir, html_templates_dict, root
    )
    gcn_handler.gcn_processor()
