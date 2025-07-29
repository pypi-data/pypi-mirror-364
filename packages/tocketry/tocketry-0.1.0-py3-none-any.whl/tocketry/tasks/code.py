from dataclasses import dataclass
from tocketry.core import Task


@dataclass(eq=False)
class CodeTask(Task):
    """Task to run a piece of Python code

    This task may be useful for APIs where a trusted
    user can create tasks or if you have your tasks stored,
    for example, in a database.

    Parameters
    ----------
    code : str
        Piece of Python code to execute. Variable ``return_value``
        is used as the return value of this task if set. Parameters
        are passed to the code as locals.
    **kwargs : dict
        See :class:`tocketry.core.Task`

    Warnings
    --------
        Note that it is potentially dangerous if you let the user
        to create CodeTasks to your system and you don't trust the
        user. The task can do anything and is practically impossible
        to restrict running non-safe code.

    Examples
    --------
    Simple example:

    .. code-block:: python

        CodeTask('''
        for i in range(10):
            ...
        ''', start_cond='daily')

    Parametrized example with return:

    .. code-block:: python

        CodeTask('''
        baz = foo + bar
        ...
        return_value = baz
        ''', parameters={'foo': 'a value', 'bar': 'a value'})
    """

    output_variable: str = "return_value"
    code: str = ""

    def execute(self, **params):
        loc = params
        glob = {}
        exec(self.code, glob, loc)
        return loc.get(self.output_variable, None)

    def __init__(self, **kwargs):
        """Initialize CodeTask by calling parent Task.__init__"""
        
        # Extract our specific fields before calling super().__init__
        code = kwargs.pop('code', '')
        output_variable = kwargs.pop('output_variable', 'return_value')
        
        # Call the parent Task's __init__ method with remaining kwargs
        super().__init__(**kwargs)
        
        # Set our specific attributes after parent initialization
        self.code = code
        self.output_variable = output_variable

    def get_default_name(self, **kwargs):
        raise ValueError("CodeTask must have name defined")
