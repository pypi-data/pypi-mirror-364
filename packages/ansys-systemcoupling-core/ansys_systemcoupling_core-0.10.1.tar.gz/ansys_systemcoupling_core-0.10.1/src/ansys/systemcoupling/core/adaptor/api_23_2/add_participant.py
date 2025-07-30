#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class add_participant(InjectedCommand):
    """
    This command operates in one of two modes, depending on how it is called.
    *Either* a single argument, ``participant_session``, should be provided, *or* some
    combination of the other optional arguments not including ``participant_session``
    should be provided.

    In the ``participant_session`` mode, the session object is queried to
    extract the information needed to define a new ``coupling_participant``
    object in the setup datamodel. A reference to the session is also retained,
    and this will play a further role if ``solve`` is called later. In that case,
    the participant solver will be driven from the Python environment in which the
    participant and PySystemCoupling sessions are active and System Coupling will
    regard the participant solver as "externally managed" (see the `execution_control`
    settings in `coupling_participant` for details of this mode).

    .. note::
        The ``participant_session`` mode currently has limited support in the
        broader Ansys Python ecosystem - at present, only PyFluent supports
        the API required of the session object and product versions of Fluent and
        System Coupling need to be at least 24.1. This capability should be
        regarded as *Beta* as it may be subject to revision when extended to other
        products.

    The remainder of the documentation describes the more usual non-session mode.

    Adds a coupling participant to the data model.

    When executed, this command adds the new participant to the analysis
    without removing any interfaces or data transfers created previously.

    Cannot be called after participants have been started.

    Returns the name of the participant.

    There are two options to add the participant - via a file, or via a
    participant executable.

    Option 1: Using an input file
        Given an input file containing participant coupling information, reads the
        specified file, pushes the participant's information to the data model.

    Option 2: Using a participant executable
        Given the path to the executable for this participant (and optionally,
        additional arguments and/or working directory), start the participant
        executable, connect to the participant using the socket connection,
        and get the participant's information and add it to the data model.

    Parameters
    ----------
    participant_session : ParticipantProtocol, optional
        Participant session object conforming to the ``ParticipantProtocol`` protocol class.
    participant_type : str, optional
        Participant type. Currently supported types are:

        - \"DEFAULT\"
        - \"CFX\"
        - \"FLUENT\"
        - \"MAPDL\"
        - \"AEDT\"
        - \"FMU\"
        - \"FORTE\"
        - \"DEFAULT-SRV\"
        - \"MECH-SRV\"
        - \"CFD-SRV\"

        If unspecified, ``add_participant`` will attempt to deduce
        the type from ``input_file``.
    input_file : str, optional
        Name of the input file for the participant to be added.
        Currently supported formats are SCP files, Forte input (FTSIM)
        files, mechanical server (*.rst) files, cfd server (*.csv) files,
        and FMU (.fmu) files (Beta).
    executable : str, optional
        Path to the executable file for the participant to be added.
    additional_arguments : str, optional
        Any additional arguments to be passed to the participant's executable.
    working_directory : str, optional
        Path to the working directory for this participant.

    """

    syc_name = "add_participant"

    cmd_name = "add_participant"

    argument_names = [
        "participant_session",
        "participant_type",
        "input_file",
        "executable",
        "additional_arguments",
        "working_directory",
    ]

    class participant_session(ParticipantSession):
        """
        Participant session object conforming to the ``ParticipantProtocol`` protocol class.
        """

        syc_name = "participant_session"

    class participant_type(String):
        """
        Participant type. Currently supported types are:

        - \"DEFAULT\"
        - \"CFX\"
        - \"FLUENT\"
        - \"MAPDL\"
        - \"AEDT\"
        - \"FMU\"
        - \"FORTE\"
        - \"DEFAULT-SRV\"
        - \"MECH-SRV\"
        - \"CFD-SRV\"

        If unspecified, ``add_participant`` will attempt to deduce
        the type from ``input_file``.
        """

        syc_name = "ParticipantType"

    class input_file(String):
        """
        Name of the input file for the participant to be added.
        Currently supported formats are SCP files, Forte input (FTSIM)
        files, mechanical server (*.rst) files, cfd server (*.csv) files,
        and FMU (.fmu) files (Beta).
        """

        syc_name = "InputFile"

    class executable(String):
        """
        Path to the executable file for the participant to be added.
        """

        syc_name = "Executable"

    class additional_arguments(String):
        """
        Any additional arguments to be passed to the participant's executable.
        """

        syc_name = "AdditionalArguments"

    class working_directory(String):
        """
        Path to the working directory for this participant.
        """

        syc_name = "WorkingDirectory"
