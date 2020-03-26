from kivy.animation import Animation
from kivy.lang import Builder
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, StringProperty, ListProperty

from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton
from kivymd.uix.behaviors import BackgroundColorBehavior
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.tooltip import MDTooltip

from graph_canvas import GraphCanvas
from constants import *


KV = '''
#:import PANEL_WIDTH constants.PANEL_WIDTH
#:import LIST_BACKGROUND constants.LIST_BACKGROUND

FloatLayout:
    GraphCanvas:
        id: graph_canvas
        adjacency_list: adjacency_list

    MDFloatingActionButton:
        id: panel_button
        icon:'forwardburger'
        md_bg_color: app.theme_cls.primary_color
        on_press: app.animate_panel()
        x: dp(10)
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

        MDTabs:
            id: side_panel
            on_tab_switch: app.on_tab_switch(*args)

            PanelTabBase:
                title: 'File'
                text: 'file-outline'
                md_bg_color: LIST_BACKGROUND

                MDRectangleFlatIconButton:
                    icon: 'eraser'
                    text: 'New graph'
                    top: self.parent.top
                    width: self.parent.width

                MDRectangleFlatIconButton:
                    icon: 'graph-outline'
                    text: 'Load graph...'
                    top: self.parent.top - self.height
                    width: self.parent.width

                MDRectangleFlatIconButton:
                    icon: 'floppy'
                    text: 'Save graph...'
                    top: self.parent.top - self.height * 2
                    width: self.parent.width

                MDRectangleFlatIconButton:
                    icon: 'language-python'
                    text: 'Load rule...'
                    top: self.parent.top - self.height * 3
                    width: self.parent.width

            PanelTabBase:
                title: 'Adjacency List'
                text: 'ray-start-arrow'
                md_bg_color: LIST_BACKGROUND

                ScrollView:
                    MDList:
                        id: adjacency_list

            PanelTabBase:
                title: 'Filters'
                text: 'filter-outline'
                md_bg_color: LIST_BACKGROUND

        MDToolbar:
            left_action_items: [['play-circle-outline', lambda _: graph_canvas.pause_callback()],\
                                ['play-box-outline', lambda _: graph_canvas.pause_layout()]]
            right_action_items: [['backburger', lambda _: app.animate_panel(-PANEL_WIDTH)]]

    BoxLayout:
        orientation: 'vertical'
        x: dp(10) + dp(4) + max(0, side_panel.right)
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
    up_color: app.theme_cls.primary_color
    down_color: app.theme_cls.primary_dark
    group: 'tools'
    allow_no_selection: False
    tooltip_text: self.label
    md_bg_color: app.theme_cls.primary_color
    tooltip_bg_color: app.theme_cls.primary_dark
    on_press: app.select_tool(self.label)
'''


class ToolIcon(MDIconButton, ToggleButtonBehavior, MDTooltip, BackgroundColorBehavior):
    label = StringProperty()
    up_color = ListProperty()
    down_color = ListProperty()

    def on_state(self, instance, value):
        self.md_bg_color = self.down_color if value == 'down' else self.up_color


class PanelTabBase(FloatLayout, MDTabsBase, BackgroundColorBehavior):
    title = StringProperty('')


class Graphvy(MDApp):
    _anim_progress = NumericProperty(-PANEL_WIDTH)

    def build(self):
        self.theme_cls.primary_hue = '900'
        return Builder.load_string(KV)

    def on_start(self):
        for node in self.root.ids.graph_canvas.nodes.values():
            self.root.ids.adjacency_list.add_widget(node.make_list_item())
        self.root.ids.grab.state = 'down'

    def on_tab_switch(self, tabs, tab, label, text):
        self.root.ids.header.title = tab.title

    def animate_panel(self, x=0):
        if x == 0:
            self.root.ids.header.title = 'Graphvy'
        Animation(_anim_progress=x, duration=.7, t='out_cubic').start(self)

    def select_tool(self, tool):
        self.root.ids.graph_canvas.tool = tool


Graphvy().run()