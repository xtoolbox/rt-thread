#
# File      : qt.py
# This file is part of RT-Thread RTOS
# COPYRIGHT (C) 2006 - 2015, RT-Thread Development Team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Change Logs:
# Date           Author       Notes
# 2017-09-22     XToolbox     Add copyright information
#

import os
import sys
import string
import building

import xml.etree.ElementTree as etree
from xml.etree.ElementTree import SubElement
from utils import _make_path_relative
from utils import xml_indent
fs_encoding = sys.getfilesystemencoding()

def Qt_AddGroup(ProjectFiles, parent, name, files, libs, project_path):
    #Filter = SubElement(parent, 'Filter')
    #Filter.set('Name', name) #set group name to group
    
    elem = parent

    for f in files:
        fn = f.rfile()
        name = fn.name
        path = os.path.dirname(fn.abspath)

        path = _make_path_relative(project_path, path)
        path = os.path.join(path, name)

        #File = SubElement(Filter, 'File')
        #File.set('RelativePath', path.decode(fs_encoding))
        path = path.decode(fs_encoding)
        elem.write('SOURCES += ' + path + '\r\n')

    for lib in libs:
        name = os.path.basename(lib)
        path = os.path.dirname(lib)

        path = _make_path_relative(project_path, path)
        path = os.path.join(path, name)

        path = path.decode(fs_encoding)
        elem.write('LIBS += ' + path + '\r\n')
        #File = SubElement(Filter, 'File')
        #File.set('RelativePath', path.decode(fs_encoding))

def Qt_AddHeadFilesGroup(program, elem, project_path):
    building.source_ext = []
    building.source_ext = ["h"]
    for item in program:
        building.walk_children(item)    
    building.source_list.sort()
    # print building.source_list
    
    for f in building.source_list:
        path = _make_path_relative(project_path, f)
        #File = SubElement(elem, 'File')
        path = path.decode(fs_encoding)
        elem.write('HEADERS += ' + path + '\r\n')
        #File.set('RelativePath', path.decode(fs_encoding))

def QtProject(target, script, program):
    project_path = os.path.dirname(os.path.abspath(target))
    
    #tree = etree.parse('template_vs2005.vcproj')
    #root = tree.getroot()
    
    out = file(target, 'wb')
    out.write('# Qt project file create by rt-thread\r\n')
    out.write('QT += core\r\n')
    out.write('TARGET = rtthread\r\n')
    out.write('TEMPLATE = app\r\n')
    out.write('CONFIG   += console\r\n')
    out.write('\r\n')
    out.write('\r\n')
    
    ProjectFiles = []
    
    # add "*.c" files group
    #for elem in tree.iter(tag='Filter'):
    #    if elem.attrib['Name'] == 'Source Files':
    #        #print elem.tag, elem.attrib
    #        break
    out.write('\r\n\r\n')
    out.write('# source files\r\n')
    for group in script:
        libs = []
        if group.has_key('LIBS') and group['LIBS']:
            for item in group['LIBS']:
                lib_path = ''
                for path_item in group['LIBPATH']:
                    full_path = os.path.join(path_item, item + '.lib')
                    if os.path.isfile(full_path): # has this library
                        lib_path = full_path

                if lib_path != '':
                    libs.append(lib_path)
        Qt_AddGroup(ProjectFiles, out, group['name'], group['src'], libs, project_path)
    
    #print 'get lib', len(libs)
    #print libs

    # add "*.h" files group
    #for elem in tree.iter(tag='Filter'):
    #    if elem.attrib['Name'] == 'Header Files':
    #        break
    out.write('\r\n\r\n')
    out.write('# head files\r\n')
    Qt_AddHeadFilesGroup(program, out, project_path)
    
    out.write('\r\n\r\n')
    out.write('# Include path\r\n')
    # write head include path
    if building.Env.has_key('CPPPATH'):
        cpp_path = building.Env['CPPPATH']
        paths  = set()
        for path in cpp_path:
            inc = _make_path_relative(project_path, os.path.normpath(path))
            paths.add(inc) #.replace('\\', '/')
    
        paths = [i for i in paths]
        paths.sort()
        cpp_path = ';'.join(paths)
        cpp_path_list = cpp_path.split(';') 
        #print "get cpp path", len(cpp_path_list)
        for e in cpp_path_list:
            out.write('INCLUDEPATH += '+e+'\r\n')
        #print cpp_path_list
        # write include path, definitions
        #for elem in tree.iter(tag='Tool'):
        #    if elem.attrib['Name'] == 'VCCLCompilerTool':
                #print elem.tag, elem.attrib
        #        break
        #elem.set('AdditionalIncludeDirectories', cpp_path)

    # write cppdefinitons flags
    out.write('\r\n\r\n')
    out.write('# defines\r\n')
    
    if building.Env.has_key('CPPDEFINES'):
        CPPDEFINES = building.Env['CPPDEFINES']
        definitions = []
        if type(CPPDEFINES[0]) == type(()):
            for item in CPPDEFINES:
                definitions += [i for i in item]
            definitions = ';'.join(definitions)
        else:
            definitions = ';'.join(building.Env['CPPDEFINES'])
        #elem.set('PreprocessorDefinitions', definitions)
        cpp_define_list = definitions.split(';')
        for e in cpp_define_list:
            out.write('DEFINES += '+e+'\r\n')
        #print "get cpp defines", len(cpp_define_list)
        #print cpp_define_list
    # write link flags

    out.write('\r\n\r\n')
    out.write('# libs\r\n')
    # write lib dependence 
    if building.Env.has_key('LIBS'):
        #for elem in tree.iter(tag='Tool'):
        #    if elem.attrib['Name'] == 'VCLinkerTool':
        #        break
        libs_with_extention = [i+'.lib' for i in building.Env['LIBS']]
        libs = ' '.join(libs_with_extention)
        #elem.set('AdditionalDependencies', libs)
        for e in libs.split(' '):
            if len(e) > 0 :
                out.write('LIBS += -l'+e+'\r\n')
        #print "get libs"
        #print '"'+libs+'"'

    # write lib include path
    out.write('# lib paths\r\n')
    if building.Env.has_key('LIBPATH'):
        lib_path = building.Env['LIBPATH']
        paths  = set()
        for path in lib_path:
            inc = _make_path_relative(project_path, os.path.normpath(path))
            paths.add(inc) #.replace('\\', '/')
    
        paths = [i for i in paths]
        paths.sort()
        lib_paths = ';'.join(paths)
        for e in lib_paths.split(';'):
            if len(e) > 0 :
                out.write('LIBS += -L'+e+'\r\n')
        #elem.set('AdditionalLibraryDirectories', lib_paths)
        #print "get lib paths"
        #print '"'+lib_paths+'"'

    #xml_indent(root)
    #out.write(etree.tostring(root, encoding='utf-8'))
    out.close()
