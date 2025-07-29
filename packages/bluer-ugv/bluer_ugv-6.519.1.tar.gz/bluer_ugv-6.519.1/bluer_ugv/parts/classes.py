from typing import List, Union, Dict, Tuple
import copy

from bluer_objects import markdown
from bluer_ugv.logger import logger


class Part:
    def __init__(
        self,
        info: Union[List[str], str] = [],
        name: str = "",
        images: List[str] = [],
    ):
        self.name = name

        self.info = (
            copy.deepcopy(info)
            if isinstance(
                info,
                list,
            )
            else [info]
        )

        self.images = (
            copy.deepcopy(images)
            if isinstance(
                images,
                list,
            )
            else [images]
        )

    @property
    def filename(self) -> str:
        return f"docs/parts/{self.name}.md"

    @property
    def README(self) -> List[str]:
        return [f"- {info}" for info in self.info] + (
            [""]
            + markdown.generate_table(
                [f"![image]({image})" for image in self.images],
                cols=3,
            )
            if self.images
            else []
        )


class PartDB:
    def __init__(self):
        self._db: Dict[str, Part] = {}

    def __iter__(self):
        return iter(self._db.values())

    def __setitem__(
        self,
        name: str,
        part: Union[Part, List[str]],
    ):
        if isinstance(part, list):
            part = Part(
                name=name,
                info=part,
            )
        else:
            part.name = name

        self._db[name] = copy.deepcopy(part)

    def __getitem__(self, name: str) -> Part:
        return self._db[name]

    @property
    def README(self) -> List[str]:
        return sorted(
            [
                "- [{}](./{}.md).".format(
                    part.info[0],
                    part.name,
                )
                for part in self
            ]
        )

    def subset(
        self,
        dict_of_parts: Dict[str, str],
        reference: str = "../../parts",
    ) -> Tuple[bool, List[str]]:
        logger.info(
            "{}.subset: {}".format(
                self.__class__.__name__,
                ", ".join(dict_of_parts.keys()),
            )
        )

        for part_name in dict_of_parts:
            if part_name not in self._db:
                logger.error(f"{part_name}: part not found.")
                return False, []

        return True, sorted(
            [
                (
                    "1. [{}{}]({}).".format(
                        self._db[part_name].info[0],
                        ": {}".format(description) if description else "",
                        f"{reference}/{part_name}.md",
                    )
                )
                for part_name, description in dict_of_parts.items()
            ]
        )
