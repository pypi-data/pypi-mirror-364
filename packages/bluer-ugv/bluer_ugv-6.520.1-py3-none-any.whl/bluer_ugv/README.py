import os

from bluer_options.help.functions import get_help
from bluer_objects import file, README

from bluer_ugv import NAME, VERSION, ICON, REPO_NAME
from bluer_ugv.help.functions import help_functions
from bluer_ugv.parts.db import db_of_parts
from bluer_ugv.sparrow.parts import dict_of_parts as sparrow_dict_of_parts
from bluer_ugv.sparrow.analog import dict_of_parts as sparrow_analog_dict_of_parts
from bluer_ugv.sparrow.README import items as sparrow_items
from bluer_ugv.swallow.parts import dict_of_parts as swallow_dict_of_parts
from bluer_ugv.swallow.README import items as swallow_items


items = README.Items(
    [
        {
            "name": "bluer_swallow",
            "marquee": "https://github.com/kamangir/assets2/blob/main/bluer-swallow/20250701_2206342_1.gif?raw=true",
            "description": "based on power wheels.",
            "url": "./bluer_ugv/docs/bluer_swallow",
        },
        {
            "name": "bluer_sparrow",
            "marquee": "https://github.com/kamangir/assets2/raw/main/bluer-sparrow/20250723_095155~2_1.gif?raw=true",
            "description": "bluer_swallow's little sister.",
            "url": "./bluer_ugv/docs/bluer_sparrow",
        },
        {
            "name": "bluer-fire",
            "marquee": "https://github.com/kamangir/assets/blob/main/bluer-ugv/bluer-fire.png?raw=true",
            "description": "based on a used car.",
            "url": "./bluer_ugv/docs/bluer_fire",
        },
        {
            "name": "bluer-beast",
            "marquee": "https://github.com/waveshareteam/ugv_rpi/raw/main/media/UGV-Rover-details-23.jpg",
            "description": "based on [UGV Beast PI ROS2](https://www.waveshare.com/wiki/UGV_Beast_PI_ROS2).",
            "url": "./bluer_ugv/docs/bluer_beast",
        },
    ]
)


def build() -> bool:
    success, sparrow_list_of_parts = db_of_parts.subset(
        sparrow_dict_of_parts,
        reference="../../../parts",
    )
    if not success:
        return success

    success, sparrow_analog_list_of_parts = db_of_parts.subset(
        sparrow_analog_dict_of_parts,
        reference="../../parts",
    )
    if not success:
        return success

    success, swallow_list_of_parts = db_of_parts.subset(
        swallow_dict_of_parts,
        reference="../../../parts",
    )
    if not success:
        return success

    return all(
        README.build(
            items=readme.get("items", []),
            path=os.path.join(file.path(__file__), readme["path"]),
            cols=readme.get("cols", 3),
            ICON=ICON,
            NAME=NAME,
            VERSION=VERSION,
            REPO_NAME=REPO_NAME,
            help_function=lambda tokens: get_help(
                tokens,
                help_functions,
                mono=True,
            ),
            macros=readme.get("macros", {}),
        )
        for readme in [
            {"path": "docs"},
            #
            {
                "items": items,
                "path": "..",
                "cols": 2,
            },
            {"path": "docs/bluer_beast"},
            {"path": "docs/bluer_fire"},
            {
                "items": swallow_items,
                "path": "docs/bluer_swallow",
            },
            {
                "items": sparrow_items,
                "path": "docs/bluer_sparrow",
                "cols": 2,
            },
            #
            {"path": "docs/bluer_swallow/analog"},
            {"path": "docs/bluer_swallow/digital"},
            {"path": "docs/bluer_swallow/digital/design"},
            {"path": "docs/bluer_swallow/digital/design/operation.md"},
            {
                "path": "docs/bluer_swallow/digital/design/parts.md",
                "macros": {"parts:::": swallow_list_of_parts},
            },
            {"path": "docs/bluer_swallow/digital/design/terraform.md"},
            {
                "path": "docs/bluer_swallow/digital/design/steering-over-current-detection.md"
            },
            {"path": "docs/bluer_swallow/digital/design/rpi-pinout.md"},
            {"path": "docs/bluer_swallow/digital/dataset"},
            {"path": "docs/bluer_swallow/digital/dataset/collection"},
            {"path": "docs/bluer_swallow/digital/dataset/collection/validation.md"},
            {"path": "docs/bluer_swallow/digital/dataset/collection/one.md"},
            {"path": "docs/bluer_swallow/digital/dataset/combination"},
            {"path": "docs/bluer_swallow/digital/dataset/combination/validation.md"},
            {"path": "docs/bluer_swallow/digital/dataset/combination/one.md"},
            {"path": "docs/bluer_swallow/digital/dataset/review.md"},
            {"path": "docs/bluer_swallow/digital/model"},
            {"path": "docs/bluer_swallow/digital/model/validation.md"},
            {"path": "docs/bluer_swallow/digital/model/one.md"},
            #
            {"path": "docs/bluer_sparrow/analog"},
            {"path": "docs/bluer_sparrow/analog/parts.md"},
            {"path": "docs/bluer_sparrow/digital"},
            {"path": "docs/bluer_sparrow/digital/design"},
            {"path": "docs/bluer_sparrow/digital/design/specs.md"},
            {
                "path": "docs/bluer_sparrow/analog/parts.md",
                "macros": {"parts:::": sparrow_analog_list_of_parts},
            },
            {
                "path": "docs/bluer_sparrow/digital/design/parts.md",
                "macros": {"parts:::": sparrow_list_of_parts},
            },
            # aliases
            {"path": "docs/aliases"},
            {"path": "docs/aliases/swallow.md"},
        ]
        # parts
        + [
            {
                "path": "docs/parts",
                "macros": {"list:::": db_of_parts.README},
            }
        ]
        + [
            {
                "path": part.filename,
                "macros": {"info:::": part.README},
            }
            for part in db_of_parts
        ]
    )
