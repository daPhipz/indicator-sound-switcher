import abc
import logging

from gi.repository import Gtk


class PreferencesDialog(Gtk.Dialog):
    """Indicator preferences dialog."""

    def __init__(self, indicator, parent: Gtk.Window=None):
        """Constructor.
        :param indicator: Sound Switcher Indicator instance
        :param parent: parent window
        """
        Gtk.Dialog.__init__(
            self, _('Sound Switcher Indicator Preferences'), parent, 0, (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE))
        self.set_border_width(12)
        self.set_default_size(600,  400)
        self.indicator = indicator

        # Add notebook with pages
        notebook = MainNotebook(indicator)
        self.get_content_area().pack_start(notebook, True, True, 0)

        # Show all controls
        self.show_all()


class BasePage(Gtk.Box):
    """Base abstract class for notebook page objects."""

    def __init__(self, title: str, indicator):
        """Constructor."""
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.set_border_width(10)
        self.scroll_box = None
        self.is_initialised = False
        self.title = title
        self.indicator = indicator

    def get_label_widget(self):
        """Create and return a widget for the page label."""
        return Gtk.Label.new_with_mnemonic(self.title)

    def on_activate(self):
        """Is called whenever the page is activated."""
        if not self.is_initialised:
            # Call the page-specific initialisation
            self.initialise()
            self.is_initialised = True

            # Show all child widgets
            self.show_all()

    @abc.abstractmethod
    def initialise(self):
        """Must initialise the page."""


class GeneralPage(BasePage):
    """General page object."""

    def __init__(self, indicator):
        super().__init__(_('_General'), indicator)

        # Add switches
        self.switch_inputs  = self._add_switch(_('Show inputs'), self.on_switch_inputs_set)
        self.switch_outputs = self._add_switch(_('Show outputs'), self.on_switch_outputs_set)

    def _add_switch(self, label: str, on_state_set: callable) -> Gtk.Switch:
        """Add a new labeled switch widget to the page.
        :return: the created switch widget
        """
        # Add a horizontal box that will hold a label and a switch
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # Add a label
        box.pack_start(Gtk.Label(label), False, False, 0)

        # Add a switch
        switch = Gtk.Switch()
        switch.connect('state-set', on_state_set)
        box.pack_end(switch, False, False, 0)

        # Add the box to the page
        self.pack_start(box, False, False, 0)
        return switch

    def initialise(self):
        self.switch_inputs.set_active (self.indicator.config['show_inputs',  True])
        self.switch_outputs.set_active(self.indicator.config['show_outputs', True])

    def on_switch_inputs_set(self, widget: Gtk.Switch, data):
        """Signal handler: Show Inputs switch set."""
        if not self.is_initialised:
            return
        logging.debug('.on_switch_inputs_set(%s)', widget.get_active())
        self.indicator.config['show_inputs'] = widget.get_active()
        self.indicator.on_refresh()

    def on_switch_outputs_set(self, widget: Gtk.Switch, data):
        """Signal handler: Show Outputs switch set."""
        if not self.is_initialised:
            return
        logging.debug('.on_switch_outputs_set(%s)', widget.get_active())
        self.indicator.config['show_outputs'] = widget.get_active()
        self.indicator.on_refresh()


class DevicesPage(BasePage):
    """Devices page object."""

    def __init__(self, indicator):
        super().__init__(_('_Devices'), indicator)

        # Add a scrollbox
        scrollbox = Gtk.ScrolledWindow()
        self.pack_start(scrollbox, True, True, 0)

        # Add a list box
        self.list_box = Gtk.ListBox()
        scrollbox.add(self.list_box)

    def initialise(self):
        for idx, card in self.indicator.cards.items():
            # Add a grid
            grid = Gtk.Grid(border_width=12, column_spacing=6, row_spacing=6)
            # -- Add an icon
            grid.attach(Gtk.Image.new_from_icon_name('yast_soundcard', Gtk.IconSize.MENU), 0, 0, 1, 2)
            # -- Add a device title label
            title_label = Gtk.Label(xalign=0)
            title_label.set_markup('<b>{}</b>'.format(card.get_display_name()))
            grid.attach(title_label, 1, 0,  1, 1)
            # -- Add a device name label
            grid.attach(Gtk.Label(card.name), 1, 1,  1, 1)
            # -- Add a configure button
            box = Gtk.Box(hexpand=True, vexpand=True)
            btn = Gtk.Button(_('Configure…'))
            btn.connect('clicked', self.on_configure_btn_clicked, idx)
            box.pack_end(btn, False, False, 0)
            grid.attach(box, 2, 1,  1, 2)

            # Add the grid as a list row
            self.list_box.add(Gtk.ListBoxRow(child=grid))

    def on_configure_btn_clicked(self, widget, idx: int):
        """Signal handler: Configure Device button clicked."""
        logging.debug('.on_configure_btn_clicked(idx=%d)', idx)
        # TODO


class MainNotebook(Gtk.Notebook):
    """Implementation of the preferences dialog's notebook control."""

    def __init__(self, indicator):
        logging.debug('Creating ' + self.__class__.__name__)
        super().__init__()

        # Create notebook pages
        self._add_page(GeneralPage(indicator))
        self._add_page(DevicesPage(indicator))

        # Connect page switch signal
        self.connect('switch-page', self.on_switch_page)

    def _add_page(self, page: BasePage):
        """Add a single (descendant of) BasePage."""
        self.append_page(page, page.get_label_widget())

    @staticmethod
    def on_switch_page(widget, page, index):
        """Signal handler: current page changed"""
        logging.debug('Page changed to %d', index)
        page.on_activate()