from dataclasses import dataclass


# analogous to Proton version
@dataclass
class Element:
    group_id: str = ""
    value: str = ""
    info: str = ""

    # proton terminology for convenience
    @property
    def dir(self):
        return self.group_id

    @property
    def version_num(self):
        return self.value

    @property
    def user_count(self):
        return self.info

    @user_count.setter
    def user_count(self, value):
        self.info = value


# analogous to Proton directory
@dataclass
class Group:
    identity: str = ""
    label: str = ""
    elements: list[Element] = list

    # proton terminology for convenience
    @property
    def path(self):
        return self.identity

    @property
    def versions(self):
        return self.elements
