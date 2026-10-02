import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: sidebar
    signal pageSelected(string page)
    signal logoutRequested()
    color: "#173b67"

    function labelFor(page) {
        if (page === "dashboard") return "Dashboard"
        if (page === "customers") return "Customers"
        if (page === "accounts") return "Accounts"
        if (page === "transactions") return "Transactions"
        if (page === "users") return "Users"
        return page
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 18

        Column {
            spacing: 2
            Layout.fillWidth: true

            Label {
                text: "BANK"
                color: "#78b7ff"
                font.pixelSize: 17
                font.bold: true
            }

            Label {
                text: "Management System"
                color: "white"
                font.pixelSize: 15
                font.bold: true
            }
        }

        Rectangle { Layout.fillWidth: true; height: 1; color: "#385b82" }

        Label {
            text: backend.role
            color: "#cfe3fa"
            font.pixelSize: 11
            font.bold: true
            Layout.fillWidth: true
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            Repeater {
                model: backend.availablePages

                delegate: Button {
                    id: navButton
                    Layout.fillWidth: true
                    implicitHeight: 42
                    text: sidebar.labelFor(modelData)
                    font.pixelSize: 14
                    contentItem: Text {
                        text: navButton.text
                        color: "white"
                        horizontalAlignment: Text.AlignLeft
                        verticalAlignment: Text.AlignVCenter
                        leftPadding: 14
                    }
                    background: Rectangle {
                        radius: 8
                        color: navButton.hovered ? "#285a8e" : "transparent"
                    }
                    onClicked: sidebar.pageSelected(modelData)
                }
            }
        }

        Item { Layout.fillHeight: true }

        Label {
            text: backend.username
            color: "#cfe3fa"
            elide: Text.ElideRight
            Layout.fillWidth: true
        }

        Button {
            id: logoutButton
            Layout.fillWidth: true
            implicitHeight: 40
            text: "Logout"
            contentItem: Text {
                text: logoutButton.text
                color: "#fecaca"
                horizontalAlignment: Text.AlignLeft
                verticalAlignment: Text.AlignVCenter
                leftPadding: 14
            }
            background: Rectangle {
                radius: 8
                color: logoutButton.hovered ? "#7f1d1d" : "transparent"
            }
            onClicked: sidebar.logoutRequested()
        }
    }
}
