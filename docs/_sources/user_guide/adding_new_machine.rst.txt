===============================
Adding a New Machine to the OTH
===============================

The following steps can be used to add support for a new system:

1. Create a machine master configuration (e.g. *lyra.ini*).
    - use the existing configs/example_machine.ini as a start
2. Create the location of the repository that will hold all applications
   and tests for that particular machine
   (*https://gitlab.ccs.ornl.gov/olcf-system-test/applications/<machine_name>*).
    - Each test will need to be added one-by-one to the new repository,
      based on the machine's capabilities.
