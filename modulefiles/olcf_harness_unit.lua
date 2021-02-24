-- -*- lua -*-

help ([[
Sets up environment to use the OLCF Test Harness.
]])

whatis("Version: 2.0") 
whatis("Repository: gitlab@gitlab.ccs.ornl.gov:olcf-system-test/olcf-test-harness.git")


-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
-- Status messages for user.
-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
local load_message = "Loading modulefile " ..  myModuleFullName() .. " ..."
local unload_message = "Unloading modulefile " ..  myModuleFullName() .. " ..."
if mode() == "load" then
    LmodMessage(load_message)
end

if mode() == "unload" then
    LmodMessage(unload_message)
end

-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
-- Start of section for loading the python
-- module
-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

-- The very first task is ensure we use Python3.
-- This load is fragile because often clusters
-- have many python module files with
-- denominations as python/X.Y.
-- Consequently one can't guarantee what python version
-- is loaded.
load("python")

-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
-- End of section for loading the python
-- module
-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
-- Start of section for modfying various
-- environmental variables - PATH, 
-- LD_LIBRARY_PATH, etc.
-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

-- Define the base path to test harness python scripts.  -
local harness = pathJoin(os.getenv('OLCF_HARNESS_DIR'),'harness')

-- Set path to harness driver programs, binaries, ...  -
setenv('PATH_TO_RGT_PACKAGE',harness)
prepend_path('PATH',pathJoin(harness,'bin'))
prepend_path('PATH',pathJoin(harness,'utilities'))
prepend_path('LD_LIBRARY_PATH',pathJoin(harness,'libraries'))
prepend_path('LIBRARY_PATH',pathJoin(harness,'libraries'))

-- Modify the PYTHONPATH
prepend_path('PYTHONPATH',pathJoin(harness,'utilities'))
prepend_path('PYTHONPATH',pathJoin(harness,'bin'))
prepend_path('PYTHONPATH',pathJoin(harness,'libraries'))
prepend_path('PYTHONPATH',pathJoin(harness))

-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
-- End of section for modfying various
-- PATHS, etc. module file.
-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
-- Start of section for loading the Sphinx 
-- module file.
-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

-- Load the Sphinx module if available. Sphinx 
-- is neeed to build the Harness Python documentation.
-- but not to run the Harness.
local sphinx_module = "sphinx/3.1.0" 
try_load(sphinx_module)
if mode() == "load" then
    if not isloaded(sphinx_module) then
        LmodMessage("WARNING! Unsucessfully loaded Sphinx module.")
        LmodMessage("The Sphinx module is not necessary to run the harness, but")
        LmodMessage("one needs the Sphinx module to build the harness documentation.")
        LmodMessage("The minimum required Sphinx version 3.1.0.")
    end
end

-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
-- End of section for loading the Sphinx 
-- module file.
-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
-- Start of section for loading the HARNESS
-- unit test module file.
-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

-- This module file is needed to run the
-- GitLab CI framework. The harness can
-- still be run without loading this module.
-- Nevertheless, we make it mandatory to 
-- enable the Gitlab unit tests.
local rt_file = "runtime_environment/GenericMachine-GenericConfigTag.unit_tests"
load(rt_file)

-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
-- End of section for loading the HARNESS
-- unit test module file.
-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
