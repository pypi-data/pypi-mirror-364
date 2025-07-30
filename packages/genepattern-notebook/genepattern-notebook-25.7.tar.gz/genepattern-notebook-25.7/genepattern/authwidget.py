import gp
from IPython.display import display
from urllib.error import HTTPError
from nbtools import UIBuilder, ToolManager, NBTool, EventManager, DataManager, Data
from .sessions import session
from .shim import login, system_message
from .jobwidget import GPJobWidget
from .taskwidget import TaskTool
from .utils import GENEPATTERN_LOGO, GENEPATTERN_SERVERS, server_name, session_color


REGISTER_EVENT = """
    const target = event.target;
    const widget = target.closest('.nbtools') || target;
    const server_input = widget.querySelector('input[type=text]');
    if (server_input) window.open(server_input.value + '/pages/registerUser.jsf');
    else console.warn('Cannot obtain GenePattern Server URL');"""


AUTO_LOGIN_CHECK = """
    const nameEQ = "GenePattern=";
    const ca = document.cookie.split(';');
    let cmatch = null;
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) cmatch = c.substring(nameEQ.length, c.length)
    }
    if (cmatch === null) return;
    const parts = cmatch.split("|");
    if (parts.length <= 1) return;
    let [u, p] = [parts[0], atob(decodeURIComponent(parts[1]))];
    this.widget_dialog({
        'title': 'Log into GenePattern Server',
        'body': 'You have already authenticated with GenePattern Cloud. Would you like to automatically sign in now?',
        'button_label': 'Login',
        'callback': () => {
            this.model.get('form').get('children')[1].get('children')[1].set('value', u);
            this.model.get('form').get('children')[1].get('children')[1].save();
            this.model.get('form').get('children')[2].get('children')[1].set('value', p);
            this.model.get('form').get('children')[2].get('children')[1].save();
            this.element.querySelector("button.nbtools-run").click();
        }
    });"""


class GPAuthWidget(UIBuilder):
    """A widget for authenticating with a GenePattern server"""
    login_spec = {  # The display values for building the login UI
        'name': 'Login',
        'collapse': False,
        'display_header': False,
        'logo': GENEPATTERN_LOGO,
        'color': session_color(),
        'run_label': 'Log into GenePattern',
        'buttons': {
            'Register an Account': REGISTER_EVENT
        },
        'events': {
            'load': AUTO_LOGIN_CHECK
        },
        'parameters': {
            'server': {
                'name': 'GenePattern Server',
                'type': 'choice',
                'combo': True,
                'sendto': False,
                'default': GENEPATTERN_SERVERS['GenePattern Cloud'],
                'choices': GENEPATTERN_SERVERS
            },
            'username': {
                'name': 'Username',
                'sendto': False,
            },
            'password': {
                'name': 'Password',
                'type': 'password',
                'sendto': False,
            }
        }
    }

    def __init__(self, session=None, **kwargs):
        """Initialize the authentication widget"""

        # Assign the session object, lazily creating one if needed
        if session is None: self.session = gp.GPServer('', '', '')
        else: self.session = session

        # Set blank token
        self.token = None

        # Check to see if the provided session has valid credentials
        if self.has_credentials() and self.validate_credentials():
            self.prepare_session()

            # Display the widget with the system message and no form
            UIBuilder.__init__(self, lambda: None, name=self.session.username, subtitle=self.session.url,
                               display_header=False, display_footer=False, color=session_color(self.session.url),
                               collapsed=True, logo=GENEPATTERN_LOGO, **kwargs)

        # If not, prompt the user to login
        else:
            # Apply the display spec
            for key, value in self.login_spec.items(): kwargs[key] = value

            # Call the superclass constructor with the spec
            UIBuilder.__init__(self, self.login, **kwargs)

    def prepare_session(self):
        """Prepare a valid session by registering the session and modules"""
        self.register_session()     # Register the session with the SessionList
        self.register_modules()     # Register the modules with the ToolManager
        self.register_jobs()        # Add recent jobs to the data panel
        self.system_message()       # Display the system message
        self.trigger_login()        # Trigger login callbacks of job and task widgets

    def login(self, server, username, password):
        """Login to the GenePattern server"""
        # Assign login values to session
        self.session.url = server
        self.session.username = username
        self.session.password = password

        # Validate the provided credentials
        if self.validate_credentials():
            self.replace_widget()
            self.prepare_session()

    def has_credentials(self):
        """Test whether the session object is instantiated and whether a username and password have been provided"""
        if type(self.session) is not gp.GPServer: return False  # Test type
        if not self.session.url: return False                   # Test server url
        if not self.session.username: return False              # Test username
        if not self.session.password: return False              # Test password
        return True

    def validate_credentials(self):
        """Call gpserver.login() to validate the provided credentials"""
        try:
            # Check to see if gp library supports login, otherwise call login shim
            if hasattr(self.session, 'login'): self.token = self.session.login()
            else: self.token = login(self.session)
            gp.core.GP_JOB_TAG = 'GenePattern Notebook'  # Set tag for jobs
            return True
        except HTTPError:
            self.error = 'Invalid username or password. Please try again.'
            return False
        except BaseException as e:
            self.error = str(e)
            return False

    def replace_widget(self):
        """Replace the unauthenticated widget with the authenticated mode"""
        self.form.form.children[2].value = ''        # Blank password so it doesn't get serialized
        self.form.collapsed = True
        self.form.name = self.session.username
        self.form.subtitle = self.session.url
        self.form.display_header=False
        self.form.display_footer=False
        self.form.form.children = []

    def register_session(self):
        """Register the validated credentials with the SessionList"""
        self.session = session.register(self.session.url, self.session.username, self.session.password)

    def register_modules(self):
        """Get the list available modules and register widgets for them with the tool manager"""
        for task in self.session.get_task_list():
            tool = TaskTool(server_name(self.session.url), task)
            ToolManager.instance().register(tool)

    def system_message(self):
        if hasattr(self.session, 'system_message'): message = self.session.system_message()
        else: message = system_message(self.session)
        self.info = message

    def trigger_login(self):
        """Dispatch a login event after authentication"""
        EventManager.instance().dispatch("gp.login", self.session)

    def register_jobs(self):
        data_list = []
        for job in self.session.get_recent_jobs():
            origin = server_name(self.session.url)
            group = f"{job.job_number}. {job.task_name}"

            # Register a custom data group widget (GPJobWidget) with the manager
            DataManager.instance().group_widget(origin=origin, group=group, widget=GPJobWidget(job))

            # Add data entries for all output files
            for file in job.get_output_files():
                data_list.append(Data(origin=origin, group=group, uri=file.get_url()))
        DataManager.instance().register_all(data_list)


class AuthenticationTool(NBTool):
    """Tool wrapper for the authentication widget"""
    origin = '+'
    id = 'authentication'
    name = 'GenePattern Login'
    description = 'Log into a GenePattern server'
    load = lambda x: GPAuthWidget()


# Register the authentication widget
ToolManager.instance().register(AuthenticationTool())

