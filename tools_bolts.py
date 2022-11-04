# ******************************************************************************
# BOLTS - Open Library of Technical Specifications                             *
#                                                                              *
# Copyright (C) 2022 Bernd Hahnebach <bernd@bimstatik.org>                     *
#                                                                              *
# This library is free software; you can redistribute it and/or                *
# modify it under the terms of the GNU Lesser General Public                   *
# License as published by the Free Software Foundation; either                 *
# version 2.1 of the License, or any later version.                            *
#                                                                              *
# This library is distributed in the hope that it will be useful,              *
# but WITHOUT ANY WARRANTY; without even the implied warranty of               *
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU             *
# Lesser General Public License for more details.                              *
#                                                                              *
# You should have received a copy of the GNU Lesser General Public             *
# License along with this library; if not, write to the Free Software          *
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA *
# ******************************************************************************


import os
import os.path
#from datetime import datetime
#from os import listdir
#from os import walk
from shutil import copyfile
#from shutil import make_archive
#from subprocess import call
#from subprocess import Popen
#from tempfile import mkstemp

from backends.license import LICENSES_SHORT
from bolttools.blt import Repository
from bolttools.drawings import DrawingsData
from bolttools.freecad import FreeCADData
from bolttools.openscad import OpenSCADData
from bolttools.pythonpackage import PythonPackageData
# from bolttools.solidworks import SolidWorksData


def export(target_backend, repo_path=None, the_license="lgpl2.1", debug=False):

    if repo_path is None:
        # TODO use the dir of this module
        return

    # load data
    repo = Repository(repo_path)
    dbs = {}
    license = LICENSES_SHORT[the_license]

    out_path = os.path.join(repo.path, "output", target_backend)
    if target_backend == "openscad":
        dbs["openscad"] = OpenSCADData(repo)
        from backends.openscad import OpenSCADBackend
        OpenSCADBackend(repo, dbs).write_output(
            out_path, target_license=license, version="development", expand=debug
        )
        copyfile(
            os.path.join(repo.path, "backends", "licenses", the_license.strip("+")),
            os.path.join(out_path, "LICENSE")
        )
    elif target_backend == "freecad":
        dbs["freecad"] = FreeCADData(repo)
        from backends.freecad import FreeCADBackend
        FreeCADBackend(repo, dbs).write_output(
            out_path, target_license=license, version="development"
        )
        copyfile(
            os.path.join(repo.path, "backends", "licenses", the_license.strip("+")),
            os.path.join(out_path, "BOLTS", "LICENSE")
        )
    elif target_backend == "pythonpackage":
        dbs["pythonpackage"] = PythonPackageData(repo)
        from backends.pythonpackage import PythonPackageBackend
        PythonPackageBackend(repo, dbs).write_output(
            out_path, target_license=license, version="development"
        )
    # elif target_backend == "solidworks":
    #     dbs["solidworks"] = SolidWorksData(repo)
    #     from backends.solidworks import SolidWorksBackend
    #     SolidWorksBackend(repo,dbs).write_output(out_path,"development")
    elif target_backend == "iges":
        dbs["freecad"] = FreeCADData(repo)
        from backends.exchange import IGESBackend
        IGESBackend(repo, dbs).write_output(out_path, "development")
    elif target_backend == "website":
        dbs["drawings"] = DrawingsData(repo)
        dbs["freecad"] = FreeCADData(repo)
        dbs["openscad"] = OpenSCADData(repo)
        from backends.webpage import WebsiteBackend
        WebsiteBackend(repo, dbs).write_output(out_path)
    elif target_backend == "drawings":
        dbs["drawings"] = DrawingsData(repo)

    return True
