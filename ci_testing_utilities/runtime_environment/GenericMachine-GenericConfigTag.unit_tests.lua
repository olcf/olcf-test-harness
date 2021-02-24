-- -*- lua -*-

-- Sourcing this file sets up the ci_testing_environment
-- for running non machine specific tests. The machine
-- specific tests runtime environment is set up if
-- the environment variables 
--      HUT_MACHINE_NAME
--      HUT_CONFIG_TAG
-- are defined - the module file ${HUT_MACHINE_NAME}-${HUT_CONFIG_TAG}
-- is loaded.

-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
-- Status messages for user.
-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
local load_message = "Loading modulefile " ..  myModuleFullName() .. " ..."
local unload_message = "Unloading modulefile " ..  myModuleFullName() .. " ..."

if ( mode() == "load" ) then
    LmodMessage(load_message)
end

if ( mode() == "unload") then
    LmodMessage(unload_message)
end

-- Set the top level directory for the CI testing directory.
local ci_testing_toplevel = pathJoin(os.getenv("OLCF_HARNESS_DIR"),'ci_testing_utilities')

-- Set the path to the CI bin directory.
local ci_testing_bin_dir =  pathJoin(ci_testing_toplevel,'bin') 

-- Add to the PYTHONPATH the CI top level directory.
prepend_path('PYTHONPATH',ci_testing_toplevel)

-- Add to the PATH varibale the generic harness unit tests.
prepend_path('PATH',ci_testing_bin_dir)

-- Load machine specific unit tests modules.

-- Check to see if environmnetal variables HUT_MACHINE_NAME 
-- HUT_CONFIG_TAG are defined. If both variables are defined
-- the load the appropriate module file.
if ( os.getenv('HUT_MACHINE_NAME') ~= nil ) and ( os.getenv('HUT_CONFIG_TAG') ~= nil ) then
    local _hutmachinename=os.getenv('HUT_MACHINE_NAME')
    local _hutconfigtag=os.getenv('HUT_CONFIG_TAG')
    local rt_file1 = _hutmachinename .. "-" .. _hutconfigtag .. ".unit_tests.lua"
    local rt_file = pathJoin('runtime_environment',rt_file1)
    try_load(rt_file)
    if not isloaded(rt_file) then
        message = "WARNING! Unsucessfully loaded machine spefic unit test module " .. rt_file .. "."
        LmodMessage(message)
    else
        message = "Sucessfully loaded machine spefic unit test module " .. rt_file .. "."
        LmodMessage(message)
    end
end
