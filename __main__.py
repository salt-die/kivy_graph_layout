from kivy.animation import Animation
from kivy.lang import Builder
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.modalview import ModalView
from kivy.properties import BooleanProperty, NumericProperty, StringProperty, ListProperty

from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton, MDRectangleFlatIconButton, MDFloatingActionButton
from kivymd.uix.behaviors import BackgroundColorBehavior, HoverBehavior
from kivymd.uix.list import MDList
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.tooltip import MDTooltip

from graph_canvas import GraphCanvas
from constants import *


KV = '''
#:import PANEL_WIDTH constants.PANEL_WIDTH
#:import NODE_COLOR constants.NODE_COLOR
#:import HIGHLIGHTED_NODE constants.HIGHLIGHTED_NODE
#:import SELECTED_COLOR constants.SELECTED_COLOR

FloatLayout:
    GraphCanvas:
        id: graph_canvas
        adjacency_list: adjacency_list

    BurgerButton:
        icon:'forwardburger'
        text_theme_color: 'Custom'
        text_color: 0, 0, 0, 1
        md_bg_color: NODE_COLOR
        on_release: app.animate_panel()
        x: dp(10) - side_panel.width/root.width - side_panel.right
        y: dp(20)

    BoxLayout:
        id: side_panel
        size_hint: PANEL_WIDTH, 1
        size_hint_min_x: 100
        size_hint_max_x: 300
        pos_hint: {'x': app._anim_progress, 'y': 0}
        orientation: 'vertical'

        MDToolbar:
            id: header
            title: 'Graphvy'
            md_bg_color: NODE_COLOR
            specific_text_color: HIGHLIGHTED_NODE

        MDTabs:
            id: tabs
            on_tab_switch: app.on_tab_switch(*args)
            background_color: NODE_COLOR
            color_indicator: HIGHLIGHTED_NODE

            PanelTabBase:
                title: 'File'
                text: 'file-outline'

                MenuItem:
                    icon: 'eraser'
                    text: 'New graph'
                    top: self.parent.top
                    on_release: graph_canvas.load_graph(random=False)

                MenuItem:
                    icon: 'vector-polyline'
                    text: 'New random graph...'
                    top: self.parent.top - self.height
                    on_release: app.erdos_reset()

                MenuItem:
                    icon: 'graph-outline'
                    text: 'Load graph...'
                    top: self.parent.top - self.height * 2
                    on_release: app.load_graph()

                MenuItem:
                    icon: 'floppy'
                    text: 'Save graph...'
                    top: self.parent.top - self.height * 3
                    on_release: app.save_graph()

                MenuItem:
                    icon: 'language-python'
                    text: 'Load rule...'
                    top: self.parent.top - self.height * 4
                    on_release: app.load_rule()

            PanelTabBase:
                title: 'Adjacency List'
                text: 'ray-start-arrow'

                ScrollView:
                    HideableList:
                        id: adjacency_list
                        is_hidden: True

            PanelTabBase:
                title: 'Filters'
                text: 'filter-outline'

        MDToolbar:
            md_bg_color: NODE_COLOR
            specific_text_color: HIGHLIGHTED_NODE
            left_action_items: [['play-circle-outline', lambda _: graph_canvas.pause_callback()],\
                                ['play-box-outline', lambda _: graph_canvas.pause_layout()]]
            right_action_items: [['backburger', lambda _: app.animate_panel(-side_panel.width/root.width)]]

    BoxLayout:
        orientation: 'vertical'
        x: dp(10) + dp(4) + side_panel.right
        y: dp(96)
        size: self.minimum_size
        spacing: dp(10)

        ToolIcon:
            id: grab
            icon: 'drag-variant'
            label: 'Grab'

        ToolIcon:
            icon: 'selection-drag'
            label: 'Select'

        ToolIcon:
            icon: 'pin'
            label: 'Pin'

        ToolIcon:
            icon: 'map-marker-path'
            label: 'Show Path'

        ToolIcon:
            icon: 'plus-circle-outline'
            label: 'Add Node'

        ToolIcon:
            icon: 'minus-circle-outline'
            label: 'Delete Node'

        ToolIcon:
            icon: 'vector-polyline-plus'
            label: 'Add Edge'

        ToolIcon:
            icon: 'vector-polyline-minus'
            label: 'Delete Edge'

<ToolIcon>:
    group: 'tools'
    allow_no_selection: False
    tooltip_text: self.label
    tooltip_text_color: NODE_COLOR
    tooltip_bg_color: SELECTED_COLOR
    theme_text_color: 'Custom'
    text_color: NODE_COLOR
    on_press: app.select_tool(self.label)

<PanelTabBase>:
    md_bg_color: SELECTED_COLOR

<MenuItem>:
    width: self.parent.width
    theme_text_color: 'Custom'
    text_color: NODE_COLOR

<RandomGraphDialogue>:
    id: random_graph_dialogue
    size_hint: .3, .2
    size_hint_min_y: dp(100)
    size_hint_max_y: dp(120)
    size_hint_max_x: dp(240)
    md_bg_color: NODE_COLOR
    GridLayout:
        padding: dp(10)
        spacing: dp(10)
        cols: 2
        rows: 2

        MDTextField:
            id: nnodes
            hint_text: 'Nodes'
            text: '50'
            size_hint: .4, .6
            on_text: random_graph_dialogue.check_if_digit(self)

        MDTextField:
            id: nedges
            hint_text: 'Edges'
            text: '80'
            size_hint: .4, .6
            on_text: random_graph_dialogue.check_if_digit(self)

        MDRaisedButton:
            text: 'OK'
            size_hint: .4, .3
            md_bg_color: HIGHLIGHTED_NODE
            text_color: NODE_COLOR
            on_release: random_graph_dialogue.new_random_graph(nnodes, nedges)

        MDFlatButton:
            text: 'Cancel'
            size_hint: .4, .3
            md_bg_color: SELECTED_COLOR
            text_color: NODE_COLOR
            on_release: random_graph_dialogue.dismiss()

<MDTextField>:
    helper_text: 'Integer required'
    helper_text_mode: 'on_error'
    required: True
    color_mode: 'custom'
    line_color_focus: HIGHLIGHTED_NODE
    pos_hint: {'center_x': .5}
    write_tab: False
'''


class HideableList(MDList):
    """List items with hover behavior are properly disabled when list is hidden."""
    is_hidden = BooleanProperty(True)


class ToolIcon(MDIconButton, ToggleButtonBehavior, MDTooltip):
    label = StringProperty()

    def on_state(self, instance, value):
        self.text_color = HIGHLIGHTED_NODE if value == 'down' else NODE_COLOR


class PanelTabBase(FloatLayout, MDTabsBase, BackgroundColorBehavior):
    title = StringProperty()


class MenuItem(MDRectangleFlatIconButton, HoverBehavior):
    def on_enter(self, *args):
        self.md_bg_color = HIGHLIGHTED_NODE

    def on_leave(self, *args):
        self.md_bg_color = SELECTED_COLOR


class BurgerButton(MDFloatingActionButton, HoverBehavior):
    def on_enter(self, *args):
        self.md_bg_color = HIGHLIGHTED_NODE

    def on_leave(self, *args):
        self.md_bg_color = NODE_COLOR


class RandomGraphDialogue(ModalView, BackgroundColorBehavior):
    def new_random_graph(self, nodes, edges):
        if nodes.text.isnumeric() and edges.text.isnumeric():
            self.graph_canvas.load_graph(random=(int(nodes.text), int(edges.text)))
            self.dismiss()
        else:
            nodes.error = not nodes.text.isnumeric()
            edges.error = not edges.text.isnumeric()

    def check_if_digit(self, widget):
        if widget.text:
            widget.error = not widget.text[-1].isdigit()
            if widget.error:
                widget.text = widget.text[:-1]


class Graphvy(MDApp):
    _anim_progress = NumericProperty(-PANEL_WIDTH)

    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        self.root.ids.grab.state = 'down'

        # Setting the text_color_active/_normal properties in kv lang appears to be bugged
        for child in self.root.ids.tabs.tab_bar.layout.children:
            child.text_color_active = HIGHLIGHTED_NODE
            child.text_color_normal = SELECTED_COLOR

        self.root.bind(width=self._resize)

    def on_tab_switch(self, tabs, tab, label, text):
        self.root.ids.header.title = tab.title

    def animate_panel(self, x=0):
        if x == 0:
            self.root.ids.header.title = 'Graphvy'
            self.root.ids.adjacency_list.is_hidden = False
        else:
            self.root.ids.adjacency_list.is_hidden = True
        Animation(_anim_progress=x, duration=.7, t='out_cubic').start(self)

    def _resize(self, *args):
        if self._anim_progress:
            self._anim_progress = -self.root.ids.side_panel.width / self.root.width

    def select_tool(self, tool):
        self.root.ids.graph_canvas.tool = tool

    def erdos_reset(self):
        dialogue = RandomGraphDialogue()
        dialogue.graph_canvas = self.root.ids.graph_canvas
        dialogue.open()

    def load_graph(self):
        print('load graph')

    def save_graph(self):
        print('save graph')

    def load_rule(self):
        print('load rule')

Graphvy().run()