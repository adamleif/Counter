import obspython as S

__version__ = "2.0.0"  # because nearly everything was rewritten, I suppose

N = 2  # default number of counters; can be updated by OBS input

class TextContent:
    def __init__(self, source_name=None, text_string="This is default text"):
        """
        Initializes the TextContent object.

        :param source_name: the name of the OBS source associated with the 
                            counter.
        :param text_string: the default text to be displayed.
        """
        self.source_name = source_name
        self.text_string = text_string
        self.counter = 0

    def update_text(self, counter_text, counter_value=0):
        """
        Updates the text of the associated OBS source.

        :param counter_text: the prefix text for the counter 
                             (e.g., "Counter: ").
        :param counter_value: the value to update the counter by (increment, 
                              decrement, or reset).
        """
        source = S.obs_get_source_by_name(self.source_name)
        settings = S.obs_data_create()

        # update the counter based on the counter_value
        if counter_value == 1:
            self.counter += 1
        if counter_value == -1:
            self.counter -= 1
        if counter_value == 0:
            self.counter = 0
        if isinstance(counter_value, str):
            self.counter = int(counter_value)

        self.text_string = f"{counter_text}{self.counter}"

        # apply the updated text to the source
        S.obs_data_set_string(settings, "text", self.text_string)
        S.obs_source_update(source, settings)
        S.obs_data_release(settings)
        S.obs_source_release(source)


class Driver(TextContent):
    def increment(self):
        self.update_text(self.counter_text, 1)

    def decrement(self):
        self.update_text(self.counter_text, -1)

    def reset(self):
        self.update_text(self.counter_text, 0)

    def do_custom(self, val):
        """
        Sets a custom value for the counter.

        :param val: the custom value to set for the counter.
        """
        self.update_text(self.counter_text, str(val))


class Hotkey:
    def __init__(self, callback, obs_settings, _id):
        """
        Initializes the Hotkey object.

        :param callback: the function to call when the hotkey is pressed.
        :param obs_settings: the OBS settings data to save/load hotkey configs.
        :param _id: the unique identifier for this hotkey.
        """
        self.obs_data = obs_settings
        self.hotkey_id = S.OBS_INVALID_HOTKEY_ID
        self.hotkey_saved_key = None
        self.callback = callback
        self._id = _id

        self.load_hotkey()
        self.register_hotkey()
        self.save_hotkey()

    def register_hotkey(self):
        """Registers the hotkey with OBS."""
        description = "Htk " + str(self._id)
        self.hotkey_id = S.obs_hotkey_register_frontend(
            "htk_id" + str(self._id), description, self.callback
        )
        S.obs_hotkey_load(self.hotkey_id, self.hotkey_saved_key)

    def load_hotkey(self):
        """Loads the saved hotkey configuration from OBS settings."""
        self.hotkey_saved_key = S.obs_data_get_array(
            self.obs_data, "htk_id" + str(self._id)
        )
        S.obs_data_array_release(self.hotkey_saved_key)

    def save_hotkey(self):
        """Saves the current hotkey configuration to OBS settings."""
        self.hotkey_saved_key = S.obs_hotkey_save(self.hotkey_id)
        S.obs_data_set_array(
            self.obs_data, "htk_id" + str(self._id), self.hotkey_saved_key
        )
        S.obs_data_array_release(self.hotkey_saved_key)


class HotkeyDataHolder:
    """
    Holder for the Hotkey instances for each counter.
    """
    htk_copy = None


def script_description():
    return "A flexible, hotkey based counter for OBS Studio."


# define counters dynamically based on N
counters = {i: Driver() for i in range(N)}  # Create N counters

# create HotkeyDataHolder instances (increment, decrement, reset), 3/counter
data_holders = {i:{j:HotkeyDataHolder() for j in range(3)} for i in 
                counters.keys()}

# -----------------------------------------------------------------------------

def create_callback_up(c):
    """
    Creates a callback for incrementing a specific counter.

    :param c: the index of the counter to increment.
    :return: a callback function for the increment hotkey.
    """
    def callback(pressed):
        if pressed: counters[c].increment()
        
    return callback


def create_callback_down(c):
    """
    Creates a callback for decrementing a specific counter.

    :param c: the index of the counter to decrement.
    :return: a callback function for the decrement hotkey.
    """
    def callback(pressed):
        if pressed: counters[c].decrement()

    return callback


def create_callback_reset(c):
    """
    Creates a callback for resetting a specific counter.

    :param c: the index of the counter to reset.
    :return: a callback function for the reset hotkey.
    """
    def callback(pressed):
        if pressed: counters[c].reset()

    return callback


def callback_custom(props, prop, settings, c):
    """
    Callback for setting a custom value for the counter when the custom input 
    field is modified.

    :param props: the properties for the script. Not utilized.
    :param prop: the specific property that was modified. Not utilized.
    :param settings: the settings for the script.
    :param c: the index of the counter being modified.
    """
    value = S.obs_data_get_int(settings, f"counter_{c}")
    counters[c].do_custom(value)
    
    return True


def script_update(settings):
    """
    Updates the script settings with the values from the OBS settings.

    :param settings: the updated settings for the script.
    """
    global N
    
    # update N based on user input
    N = S.obs_data_get_int(settings, "num_counters")

    # re-create counters dynamically based on the new value of N
    global counters
    counters = {i: Driver() for i in range(N)}

    for c in counters:
        counters[c].source_name = S.obs_data_get_string(
            settings, f"source_{c}")
        counters[c].counter_text = S.obs_data_get_string(
            settings, f"counter_text{c}")


def script_properties():
    """
    Defines the properties (inputs) for the script configuration in the OBS UI.

    :return: the properties for the script.
    """
    props = S.obs_properties_create()
    ps = []

    # add a property to set the number of counters dynamically
    S.obs_properties_add_int(
        props, "num_counters", "Number of Counters", 1, 100, 1
    )

    for c in counters:
        # add the counter text field for each counter
        S.obs_properties_add_text(
            props, f"counter_text{c}", f"[{c}] Counter Frontmatter",
            S.OBS_TEXT_DEFAULT
        )

        # add the custom value input field for each counter
        p = S.obs_properties_add_int(
            props, f"counter_{c}", f"[{c}] Set Custom Value", -999999, 999999, 
            1
        )

        # set the callback for the custom value input field
        S.obs_property_set_modified_callback(
            p, lambda props, prop, settings, c=c: 
                callback_custom(props, prop, settings, c)
        )

        # add the text source dropdown for each counter
        ps.append(
            S.obs_properties_add_list(
                props,
                f"source_{c}",
                f"[{c}] Text Source",
                S.OBS_COMBO_TYPE_EDITABLE,
                S.OBS_COMBO_FORMAT_STRING,
            )
        )

    # populate the source dropdown with available text sources in OBS
    sources = S.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = S.obs_source_get_unversioned_id(source)
            if source_id == "text_gdiplus" or source_id == "text_ft2_source":
                name = S.obs_source_get_name(source)
                for p in ps:
                    S.obs_property_list_add_string(p, name, name)

        S.source_list_release(sources)

    return props


def script_load(settings):
    """
    Loads the settings for the script, including counter values and hotkey 
    configurations.

    :param settings: The settings to load.
    """
    global N
    N = S.obs_data_get_int(settings, "num_counters")  # load N from settings

    # re-create counters based on the new value of N
    global counters
    counters = {i:Driver() for i in range(N)}

    # re-create data_holders with the new value of N
    global data_holders
    data_holders = {i:{j:HotkeyDataHolder() for j in range(3)} for i in 
                    range(N)}

    for c in counters:
        counters[c].counter = S.obs_data_get_int(settings, f"counter_{c}")
        data_holders[c][0].htk_copy = Hotkey(
            create_callback_up(c), settings, f"count_up{c}")
        data_holders[c][1].htk_copy = Hotkey(
            create_callback_down(c), settings, f"count_down{c}")
        data_holders[c][2].htk_copy = Hotkey(
            create_callback_reset(c), settings, f"count_reset{c}")


def script_save(settings):
    """
    Saves the settings for the script, including counter values and hotkey 
    configurations.

    :param settings: The settings to save.
    """
    for c in counters:
        S.obs_data_set_int(settings, f"counter_{c}", counters[c].counter)
        for h in data_holders[c]:
            data_holders[c][h].htk_copy.save_hotkey()


description = """
<h2>Version : {__version__}</h2>
<a href="https://github.com/adamleif/Counter"> Webpage </a>
<h3 style="color:orange">Authors</h3>
<a href="https://github.com/upgradeQ"> upgradeQ </a> <br>
<a href="https://github.com/adamleif"> adamleif </a> <br>
""".format(**locals())


def script_description():
    """
    Returns the description of the script, including version and author 
    information.

    :return: The description of the script.
    """
    print(description, "Released under MIT license")
    return description
