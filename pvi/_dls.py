import csv
import io
from io import StringIO

from ruamel.yaml import YAML

from ._types import AsynParameter, ChannelConfig, Formatter, Group, Record, Tree, walk
from ._util import get_param_set, prepare_for_yaml
from .adl_utils import GenerateADL
from .edl_utils import GenerateEDL

FIELD_TXT = '    field({0:5s} "{1}")\n'
INFO_TXT = '    info({0} "{1}")\n'


class DLSFormatter(Formatter):
    def format_adl(
        self, channels: Tree[ChannelConfig], basename: str, _schema: dict
    ) -> str:
        screen = GenerateADL(
            w=0,
            h=900,
            x=5,
            y=40,
            box_y=0,
            box_h=0,
            box_x=0,
            box_w=300,
            box_column=300,
            box_title=20,
            margin=5,
            label_counter=0,
            label_height=23,
            widget_height=19,
            widget_width=0,
        )
        boxes = ""
        widgets = ""
        child_nodes = 0
        for channel in walk(channels):
            if isinstance(channel, Group):
                child_nodes = len(channel.children)
                boxes += screen.make_box(
                    box_label=channel.get_label(), nodes=child_nodes
                )
            else:
                widgets += screen.make_widget(
                    nodes=child_nodes,
                    widget_label=channel.get_label(),
                    widget_type=channel.widget,
                    read_pv=channel.read_pv,
                    write_pv=channel.write_pv,
                )
        main_window = screen.make_main_window(window_title=basename)
        edm_out = main_window + boxes + widgets
        return edm_out

    def format_edl(
        self, channels: Tree[ChannelConfig], basename: str, _schema: dict
    ) -> str:
        screen = GenerateEDL(
            w=0,
            h=900,
            x=5,
            y=50,
            max_box_h=800,
            box_y=50,
            box_h=0,
            box_x=5,
            box_w=265,
            box_column=265,
            max_nodes=0,
            margin=5,
            column_counter=0,
            label_reset=0,
            label_counter=0,
            label_height=20,
            label_width=115,
            widget_height=17,
            widget_width=0,
            widget_dist=112,
            exit_space=50,
            def_font_class="arial",
            def_fg_colour_ctrl=25,
            def_bg_colour_ctrl=3,
            def_fg_colour_mon=16,
            def_bg_colour_mon=10,
        )
        boxes = ""
        widgets = ""
        child_nodes = 0
        for channel in walk(channels):
            if isinstance(channel, Group):
                child_nodes = len(channel.children)
                boxes += screen.make_box(
                    box_label=channel.get_label(), nodes=child_nodes
                )
            else:
                widgets += screen.make_widget(
                    nodes=child_nodes,
                    widget_label=channel.get_label(),
                    widget_type=channel.widget,
                    read_pv=channel.read_pv,
                    write_pv=channel.write_pv,
                )
        main_window = screen.make_main_window(window_title=basename)
        exit_button = screen.make_exit_button()
        edm_out = main_window + boxes + widgets + exit_button
        return edm_out

    def format_yaml(
        self, channels: Tree[ChannelConfig], _basename: str, _schema: dict
    ) -> str:
        # Walk the tree stripping enums and preserving descriptions
        children = [prepare_for_yaml(c.dict(exclude_none=True)) for c in channels]
        stream = StringIO()
        YAML().dump(dict(children=children), stream)
        return stream.getvalue()

    def format_csv(
        self, channels: Tree[ChannelConfig], _basename: str, _schema: dict
    ) -> str:
        out = io.StringIO(newline="")
        writer = csv.writer(out, delimiter=",", quotechar='"')
        writer.writerow(["Parameter", "PVs", "Description"])
        for channel in walk(channels):
            if isinstance(channel, Group):
                writer.writerow([f"*{channel.name}*"])
            else:
                # Filter out PVs that are None
                pvs = "\n".join(filter(None, [channel.write_pv, channel.read_pv]))
                writer.writerow([channel.name, pvs, channel.description])
        return out.getvalue()

    def format_template(
        self, records: Tree[Record], basename: str, schema: dict
    ) -> str:
        txt = ""
        for record in walk(records):
            if isinstance(record, Group):
                txt += f"# Group: {record.name}\n\n"
            else:
                fields = ""
                for k, v in record.fields_.items():
                    fields += FIELD_TXT.format(k + ",", v)
                for k, v in record.infos.items():
                    fields += INFO_TXT.format(k + ",", v)
                txt += f"""\
record({record.type}, "{record.name}") {{
{fields.rstrip()}
}}

"""
        return txt

    def format_h(
        self, parameters: Tree[AsynParameter], basename: str, schema: dict
    ) -> str:
        parent_param_set = get_param_set(schema.parent)

        parameter_definitions = [
            dict(
                name=basename.capitalize() + node.name,
                string_name=f"{node.index_name}String",
                type=node.type,
                index_name=node.index_name,
                drv_info=node.drv_info,
            )
            for node in walk(parameters)
            if isinstance(node, AsynParameter)
        ]

        defines = "\n".join(
            '#define {string_name} "{drv_info}"'.format(**definition)
            for definition in parameter_definitions
        )

        adds = "\n".join(
            "        this->add({string_name}, {type}, &{index_name});".format(
                **definition
            )
            for definition in parameter_definitions
        )

        _indexes = [
            "    int {index_name};".format(**definition)
            for definition in parameter_definitions
        ]
        _indexes.insert(
            1,
            "    #define FIRST_{basename}PARAMSET_PARAM {index_name}".format(
                basename=basename.upper(), **parameter_definitions[0]
            ),
        )
        indexes = "\n".join(_indexes)

        h_txt = f"""\
#ifndef {basename[0].upper() + basename[1:]}ParamSet_H
#define {basename[0].upper() + basename[1:]}ParamSet_H

#include "{parent_param_set}.h"

{defines}

class {basename}ParamSet : public virtual {parent_param_set} {{
public:
    {basename}ParamSet() {{
{adds}
    }}

{indexes}
}};

#endif // {basename[0].upper() + basename[1:]}ParamSet_H
"""
        return h_txt
