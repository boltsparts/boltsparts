# BOLTS - Open Library of Technical Specifications
# Copyright (C) 2013 Johannes Reinhardt <jreinhardt@ist-dein-freund.de>
# Copyright (C) 2021 Bernd Hahnebach <bernd@bimstatik.org>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import importlib
import sys
from os.path import dirname
from os.path import join

from PySide import QtCore
from PySide import QtGui
from PySide.QtCore import Slot

import FreeCAD
import FreeCADGui
from FreeCADGui import PySideUic as uic

from ..app.freecad_bolts_app import add_part_to_doc
from ..bolttools import freecad
from ..bolttools.blt import Collection
from ..bolttools.blt import ClassName
from ..bolttools.blt import ClassStandard


bolts_path = dirname(__file__)  # ui path


def unpack(x):
    return x


# custom widgets
class PropertyWidget(QtGui.QWidget):
    def __init__(self, parent, prop, value):
        super(PropertyWidget, self).__init__()
        self.ui = uic.loadUi(join(bolts_path, "property_widget.ui"))
        self.ui.prop.setTextFormat(QtCore.Qt.RichText)
        self.ui.prop.setText("<b>%s:</b>" % prop)
        self.ui.value.setText(value)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)


class LengthWidget(QtGui.QWidget):
    def __init__(self, parent, label, default):
        super(LengthWidget, self).__init__()
        self.ui = uic.loadUi(join(bolts_path, "value_widget.ui"))
        self.ui.label.setText(label)
        self.ui.valueEdit.setText(default)

        self.validator = QtGui.QDoubleValidator(
            0, sys.float_info.max, 4, self
        )
        self.ui.valueEdit.setValidator(self.validator)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

    def getValue(self):
        return float(self.ui.valueEdit.text())


class NumberWidget(QtGui.QWidget):
    def __init__(self, parent, label, default):
        super(NumberWidget, self).__init__()
        self.ui = uic.loadUi(join(bolts_path, "value_widget.ui"))
        self.ui.label.setText(label)
        self.ui.valueEdit.setText(default)

        self.validator = QtGui.QDoubleValidator(self)
        self.ui.valueEdit.setValidator(self.validator)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

    def getValue(self):
        return float(self.ui.valueEdit.text())


class AngleWidget(QtGui.QWidget):
    def __init__(self, parent, label, default):
        super(AngleWidget, self).__init__()
        self.ui = uic.loadUi(join(bolts_path, "value_widget.ui"))
        self.ui.label.setText(label)
        self.ui.valueEdit.setText(default)

        self.validator = QtGui.QDoubleValidator(self)
        self.validator.setRange(-360., 360., 2)
        self.ui.valueEdit.setValidator(self.validator)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)
    def getValue(self):
        return float(self.ui.valueEdit.text())


class StringWidget(QtGui.QWidget):
    def __init__(self, parent, label, default):
        super(StringWidget, self).__init__()
        self.ui = uic.loadUi(join(bolts_path, "value_widget.ui"))
        self.ui.label.setText(label)
        self.ui.valueEdit.setText(default)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

    def getValue(self):
        return self.ui.valueEdit.text()


class BoolWidget(QtGui.QWidget):
    def __init__(self, parent, label, default):
        super(BoolWidget, self).__init__()
        self.ui = uic.loadUi(join(bolts_path, "bool_widget.ui"))
        self.ui.checkBox.setText(label)
        if default == "True":
            self.ui.checkBox.setChecked(True)
        else:
            self.ui.checkBox.setChecked(False)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

    def getValue(self):
        return self.ui.checkBox.isChecked()


class TableIndexWidget(QtGui.QWidget):
    def __init__(self, parent, label, keys, default):
        super(TableIndexWidget, self).__init__()
        self.ui = uic.loadUi(join(bolts_path, "tableindex_widget.ui"))
        self.ui.label.setText(label)

        for key, i in zip(keys, range(len(keys))):
            self.ui.comboBox.addItem(key)
            if key == default:
                self.ui.comboBox.setCurrentIndex(i)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

    def getValue(self):
        return str(self.ui.comboBox.currentText())


class BoltsWidget(QtGui.QWidget):
    def __init__(self, repo, freecad_db):
        super(BoltsWidget, self).__init__()
        self.ui = uic.loadUi(join(bolts_path, 'bolts_widget.ui'))

        self.repo = repo
        self.dbs = {}
        self.dbs["freecad"] = freecad_db

        self.param_widgets = {}
        self.props_widgets = {}

        self.coll_root = QtGui.QTreeWidgetItem(
            self.ui.partsTree,
            ["Collections", "Ordered by collections"]
        )
        self.coll_root.setData(0, 32, None)
        self.std_root = QtGui.QTreeWidgetItem(
            self.ui.partsTree,
            ["Standard", "Ordered by issuing body"]
        )
        self.std_root.setData(0, 32, None)

        # set up collections
        for coll, in self.repo.itercollections():
            coll_item = QtGui.QTreeWidgetItem(
                self.coll_root,
                [coll.name, coll.description]
            )
            coll_item.setData(0, 32, coll)

            multinames = {}
            multistds = {}

            clasids = []
            # names
            for name, multiname in self.dbs["freecad"].iternames(
                ["name", "multiname"], filter_collection=coll
            ):
                # append classid
                clasids.append(self.repo.class_names.get_src(name).id)
                item = None
                if multiname is None:
                    item = QtGui.QTreeWidgetItem(
                        coll_item,
                        [name.name.get_nice(), name.description]
                    )
                else:
                    if multiname not in multinames:
                        multinames[multiname] = QtGui.QTreeWidgetItem(
                            coll_item,
                            [multiname.group.get_nice(), ""]
                        )
                    item = QtGui.QTreeWidgetItem(
                        multinames[multiname],
                        [name.name.get_nice(), name.description]
                    )

                item.setData(0, 32, name)

            # single names
            for std, multistd in self.dbs["freecad"].iterstandards(
                ["standard", "multistandard"], filter_collection=coll
            ):
                item = None
                # only add item if it is not in classids
                if self.repo.class_standards.get_src(std).id not in clasids:
                    if multistd is None:
                        item = QtGui.QTreeWidgetItem(
                            coll_item,
                            [std.standard.get_nice(), std.description]
                        )
                    else:
                        if multistd not in multistds:
                            multistds[multistd] = QtGui.QTreeWidgetItem(
                                coll_item,
                                [multistd.standard.get_nice(), ""]
                            )
                        item = QtGui.QTreeWidgetItem(
                            multistds[multistd],
                            [std.standard.get_nice(), std.description]
                        )

                    item.setData(0, 32, std)

        multistds = {}

        # set up standards
        for body, in repo.iterbodies():
            std_item = QtGui.QTreeWidgetItem(
                self.std_root,
                [body.body, "Standards issued by %s" % body.body]
            )
            std_item.setData(0, 32, None)
            # single standards
            for std, multistd in self.dbs["freecad"].iterstandards(
                ["standard", "multistandard"], filter_body=body
            ):
                if multistd is None:
                    item = QtGui.QTreeWidgetItem(
                        std_item,
                        [std.standard.get_nice(), std.description]
                    )
                else:
                    if multistd not in multistds:
                        multistds[multistd] = QtGui.QTreeWidgetItem(
                            std_item,
                            [multistd.standard.get_nice(), ""]
                        )
                    item = QtGui.QTreeWidgetItem(
                        multistds[multistd],
                        [std.standard.get_nice(), std.description]
                    )

                item.setData(0, 32, std)

        self.remove_empty_items(self.coll_root)

        # connections
        self.ui.addButton.clicked.connect(self.add_button_clicked)
        self.ui.partsTree.clicked.connect(self.parts_tree_sel_changed)

        # main layout for self.ui
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

    def remove_empty_items(self, root_item):
        children = [root_item.child(i) for i in range(root_item.childCount())]
        for child in children:
            self.remove_empty_items(child)
            data = unpack(child.data(0, 32))
            if (
                not (
                    isinstance(data, ClassName)
                    or isinstance(data, ClassStandard)
                )
                and child.childCount() == 0
            ):
                root_item.removeChild(child)

    def setup_param_widgets(self, cl, base):
        # print("construct param widgets")
        # construct widgets
        params = cl.parameters.union(base.parameters)

        for p in params.free:
            p_type = params.types[p]
            default = str(params.defaults[p])
            if p_type == "Length (mm)":
                self.param_widgets[p] = LengthWidget(
                    self.ui.params, p + " (mm)", default
                )
            elif p_type == "Length (in)":
                self.param_widgets[p] = LengthWidget(
                    self.ui.params, p + " (in)", default
                )
            elif p_type == "Number":
                self.param_widgets[p] = NumberWidget(
                    self.ui.params, p, default
                )
            elif p_type == "Angle (deg)":
                self.param_widgets[p] = AngleWidget(
                    self.ui.params, p + " (deg)", default
                )
            elif p_type == "Bool":
                self.param_widgets[p] = BoolWidget(
                    self.ui.params, p, default
                )
            elif p_type == "Table Index":
                self.param_widgets[p] = TableIndexWidget(
                    self.ui.params, p, params.choices[p], default
                )
            else:
                raise ValueError(
                    "Unknown type encountered for parameter %s: %s"
                    % (p, p_type)
                )
            self.param_widgets[p].setToolTip(params.description[p])

            # add them to layout
            self.ui.param_layout.addWidget(self.param_widgets[p])
        if base.type == "fcstd":
            self.ui.addButton.setText("Add part (may take a bit)")
        else:
            self.ui.addButton.setText("Add part")

    def setup_props_collection(self, coll):
        # construct widgets
        self.props_widgets.append(PropertyWidget(
            self.ui.props, "Name", coll.name
        ))
        self.props_widgets.append(PropertyWidget(
            self.ui.props, "Description", coll.description
        ))
        self.props_widgets.append(PropertyWidget(
            self.ui.props, "Authors", ", ".join(coll.author_names)
        ))
        self.props_widgets.append(PropertyWidget(
            self.ui.props, "License", coll.license_name
        ))

        # add them to layout
        for widget in self.props_widgets:
            self.ui.props_layout.addWidget(widget)

    def setup_props_standard(self, std):
        # construct widgets
        self.props_widgets.append(PropertyWidget(
            self.ui.props, "Name", std.standard.get_nice()
        ))
        if std.description:
            self.props_widgets.append(PropertyWidget(
                self.ui.props, "Description", std.description
            ))
        if std.status == "withdrawn":
            self.props_widgets.append(PropertyWidget(
                self.ui.props,
                "Status",
                "<font color='red'>%s</font>" % std.status
            ))
        else:
            self.props_widgets.append(PropertyWidget(
                self.ui.props,
                "Status",
                "<font color='green'>%s</font>" % std.status
            ))
        if std.replaces is not None:
            self.props_widgets.append(PropertyWidget(
                self.ui.props, "Replaces", std.replaces
            ))
        if std.replacedby is not None:
            self.props_widgets.append(PropertyWidget(
                self.ui.props, "Replacedby", std.replacedby
            ))
        self.props_widgets.append(PropertyWidget(
            self.ui.props, "ID", std.get_id()
        ))

        # add them to layout
        for widget in self.props_widgets:
            self.ui.props_layout.addWidget(widget)

    def setup_props_name(self, name):
        # construct widgets
        self.props_widgets.append(PropertyWidget(
            self.ui.props, "Name", name.name.get_nice()
        ))
        if name.description:
            self.props_widgets.append(PropertyWidget(
                self.ui.props, "Description", name.description
            ))
        self.props_widgets.append(PropertyWidget(
            self.ui.props, "ID", name.get_id()
        ))

        # add them to layout
        for widget in self.props_widgets:
            self.ui.props_layout.addWidget(widget)

    def add_button_clicked(self):
        # print("add button clicked")
        items = self.ui.partsTree.selectedItems()

        if len(items) < 1:
            return

        if FreeCAD.activeDocument() is None:
            FreeCAD.newDocument()

        data = unpack(items[0].data(0, 32))

        if isinstance(data, ClassName):
            cl = self.repo.class_names.get_src(data)
        elif isinstance(data, ClassStandard):
            cl = self.repo.class_standards.get_src(data)
        else:
            return

        params = {}
        # read parameters from widgets
        for key in self.param_widgets:
            params[key] = self.param_widgets[key].getValue()
        params = cl.parameters.collect(params)

        params["name"] = data.labeling.get_nice(params)

        lengths = {"Length (mm)": "mm", "Length (in)": "in"}

        for key, tp in cl.parameters.types.items():
            if tp in lengths:
                if params[key] is None:
                    # A undefined value is not necessarily fatal
                    continue
                if hasattr(FreeCAD.Units, "parseQuantity"):
                    params[key] = FreeCAD.Units.parseQuantity(
                        "%g %s" % (params[key], lengths[tp])
                    ).Value
                else:
                    params[key] = FreeCAD.Units.translateUnit(
                        "%g %s" % (params[key], lengths[tp])
                    )

        # add part
        try:
            base = self.dbs["freecad"].base_classes.get_src(cl)
            coll = self.repo.collection_classes.get_src(cl)
            add_part_to_doc(coll, base, params, FreeCAD.ActiveDocument)
            FreeCADGui.SendMsgToActiveView("ViewFit")
            FreeCAD.ActiveDocument.recompute()
        except ValueError as e:
            QtGui.QErrorMessage(self).showMessage(str(e))
        except Exception as e:
            FreeCAD.Console.PrintMessage(e)
            QtGui.QErrorMessage(self).showMessage(
                "An error occurred when trying to add the part: "
                "%s\nParameter Values: %s"
                % (e, params)
            )

    def parts_tree_sel_changed(self):
        # print("parts tree selection changed")
        items = self.ui.partsTree.selectedItems()
        if len(items) < 1:
            return
        item = items[0]
        data = unpack(item.data(0, 32))

        # clear props widget
        for widget in self.props_widgets:
            self.ui.props_layout.removeWidget(widget)
            widget.setParent(None)
        self.props_widgets = []
        # clear
        for key in self.param_widgets:
            self.ui.param_layout.removeWidget(self.param_widgets[key])
            self.param_widgets[key].setParent(None)
        self.param_widgets = {}

        if isinstance(data, ClassName):
            self.setup_props_name(data)
            cl = self.repo.class_names.get_src(data)
            base = self.dbs["freecad"].base_classes.get_src(cl)
            print(self.dbs["freecad"])
            self.setup_param_widgets(cl, base)
        elif isinstance(data, ClassStandard):
            self.setup_props_standard(data)
            cl = self.repo.class_standards.get_src(data)
            base = self.dbs["freecad"].base_classes.get_src(cl)
            self.setup_param_widgets(cl, base)
        elif isinstance(data, Collection):
            self.setup_props_collection(data)
