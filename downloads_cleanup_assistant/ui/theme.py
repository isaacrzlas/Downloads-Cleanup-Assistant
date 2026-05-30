"""Light and dark theme stylesheets."""

from __future__ import annotations


LIGHT_STYLE = """
QMainWindow, QWidget#AppRoot, QWidget#StackPage {
    background: #f5f7f6;
    color: #18201c;
    font-family: "Segoe UI", "Inter", "Roboto", sans-serif;
    font-size: 10pt;
}
QWidget {
    color: #18201c;
    font-family: "Segoe UI", "Inter", "Roboto", sans-serif;
    font-size: 10pt;
}
QLabel {
    background: transparent;
}
QMenuBar {
    background: #ffffff;
    border-bottom: 1px solid #e4e8e5;
    padding: 4px;
}
QFrame#Header, QFrame#Footer {
    background: #ffffff;
    border: 1px solid #e4e8e5;
    border-radius: 8px;
}
QLabel#AppTitle {
    font-size: 22pt;
    font-weight: 800;
    color: #142119;
}
QLabel#SectionTitle {
    font-size: 15pt;
    font-weight: 750;
}
QLabel#Muted {
    color: #69736d;
}
QFrame#StatCard, QFrame#RecommendationCard, QFrame#WelcomePanel {
    background: #ffffff;
    border: 1px solid #e2e8e4;
    border-radius: 8px;
}
QFrame#WelcomeBullets {
    background: #f7faf8;
    border: 1px solid #e4eae6;
    border-radius: 8px;
}
QFrame#StatCard:hover, QFrame#RecommendationCard:hover {
    border-color: #24a667;
    background: #fbfffd;
}
QLabel#StatValue {
    font-size: 20pt;
    font-weight: 800;
    color: #167348;
}
QPushButton {
    background: #ffffff;
    border: 1px solid #d8dfda;
    border-radius: 7px;
    padding: 8px 12px;
    font-weight: 650;
}
QPushButton:hover {
    border-color: #24a667;
    background: #f2fbf6;
}
QPushButton:disabled {
    color: #9aa39e;
    background: #eef1ef;
}
QPushButton#PrimaryButton {
    color: white;
    background: #168f55;
    border-color: #168f55;
}
QPushButton#PrimaryButton:hover {
    background: #117a48;
}
QPushButton#DangerButton {
    color: white;
    background: #b84a4a;
    border-color: #b84a4a;
}
QLineEdit, QComboBox, QSpinBox {
    background: #ffffff;
    border: 1px solid #d8dfda;
    border-radius: 7px;
    padding: 7px 9px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border-color: #24a667;
}
QTabWidget::pane {
    border: 1px solid #e2e8e4;
    background: #ffffff;
    border-radius: 8px;
}
QTabBar::tab {
    background: transparent;
    padding: 10px 16px;
    margin-right: 2px;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    font-weight: 650;
}
QTabBar::tab:selected {
    background: #ffffff;
    color: #167348;
    border: 1px solid #e2e8e4;
    border-bottom: 1px solid #ffffff;
}
QTableView {
    background: #ffffff;
    alternate-background-color: #f7faf8;
    border: none;
    gridline-color: #ebefec;
    selection-background-color: #dff5e9;
    selection-color: #122016;
}
QHeaderView::section {
    background: #f0f4f1;
    border: none;
    border-right: 1px solid #dde5df;
    padding: 9px;
    font-weight: 700;
}
QProgressBar {
    border: 1px solid #d8dfda;
    border-radius: 6px;
    text-align: center;
    background: #eef2ef;
}
QProgressBar::chunk {
    background: #24a667;
    border-radius: 5px;
}
"""


DARK_STYLE = """
QMainWindow, QWidget#AppRoot, QWidget#StackPage {
    background: #101412;
    color: #edf5f0;
    font-family: "Segoe UI", "Inter", "Roboto", sans-serif;
    font-size: 10pt;
}
QWidget {
    color: #edf5f0;
    font-family: "Segoe UI", "Inter", "Roboto", sans-serif;
    font-size: 10pt;
}
QLabel {
    background: transparent;
}
QMenuBar {
    background: #171d1a;
    color: #edf5f0;
    border-bottom: 1px solid #26302b;
    padding: 4px;
}
QFrame#Header, QFrame#Footer {
    background: #171d1a;
    border: 1px solid #26302b;
    border-radius: 8px;
}
QLabel#AppTitle {
    font-size: 22pt;
    font-weight: 800;
    color: #f4fff8;
}
QLabel#SectionTitle {
    font-size: 15pt;
    font-weight: 750;
}
QLabel#Muted {
    color: #a7b4ac;
}
QFrame#StatCard, QFrame#RecommendationCard, QFrame#WelcomePanel {
    background: #171d1a;
    border: 1px solid #27332d;
    border-radius: 8px;
}
QFrame#WelcomeBullets {
    background: #141a17;
    border: 1px solid #27332d;
    border-radius: 8px;
}
QFrame#StatCard:hover, QFrame#RecommendationCard:hover {
    border-color: #34c77a;
    background: #19231e;
}
QLabel#StatValue {
    font-size: 20pt;
    font-weight: 800;
    color: #5ce095;
}
QPushButton {
    background: #1b231f;
    color: #edf5f0;
    border: 1px solid #344139;
    border-radius: 7px;
    padding: 8px 12px;
    font-weight: 650;
}
QPushButton:hover {
    border-color: #34c77a;
    background: #213027;
}
QPushButton:disabled {
    color: #68746d;
    background: #18201c;
}
QPushButton#PrimaryButton {
    color: #07120c;
    background: #5ce095;
    border-color: #5ce095;
}
QPushButton#PrimaryButton:hover {
    background: #42cd80;
}
QPushButton#DangerButton {
    color: white;
    background: #b84a4a;
    border-color: #b84a4a;
}
QLineEdit, QComboBox, QSpinBox {
    background: #151b18;
    color: #edf5f0;
    border: 1px solid #344139;
    border-radius: 7px;
    padding: 7px 9px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border-color: #34c77a;
}
QTabWidget::pane {
    border: 1px solid #27332d;
    background: #171d1a;
    border-radius: 8px;
}
QTabBar::tab {
    background: transparent;
    padding: 10px 16px;
    margin-right: 2px;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    font-weight: 650;
}
QTabBar::tab:selected {
    background: #171d1a;
    color: #5ce095;
    border: 1px solid #27332d;
    border-bottom: 1px solid #171d1a;
}
QTableView {
    background: #171d1a;
    alternate-background-color: #141a17;
    border: none;
    gridline-color: #26302b;
    selection-background-color: #265a3e;
    selection-color: #ffffff;
}
QHeaderView::section {
    background: #1d2621;
    border: none;
    border-right: 1px solid #2b3831;
    padding: 9px;
    font-weight: 700;
}
QProgressBar {
    border: 1px solid #344139;
    border-radius: 6px;
    text-align: center;
    background: #151b18;
}
QProgressBar::chunk {
    background: #5ce095;
    border-radius: 5px;
}
"""
