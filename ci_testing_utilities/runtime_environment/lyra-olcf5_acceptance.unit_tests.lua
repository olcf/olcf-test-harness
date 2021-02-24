-- -*- lua -*-
whatis([[Name : OLCH Harness Unit Tests]])
load_message = "Loading modulefile " ..  myModuleFullName() .. " ..."
unload_message = "Unloading modulefile " ..  myModuleFullName() .. " ..."

-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
-- Status messages for user.
-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
if mode() == "load" then
    LmodMessage(load_message)
end

if mode() == "unload" then
    LmodMessage(unload_message)
end
