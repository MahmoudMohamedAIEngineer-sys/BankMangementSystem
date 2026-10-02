import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "components"

Item {
    anchors.fill: parent

    Rectangle {
        anchors.fill: parent
        color: "#eef3f9"

        Rectangle {
            width: 880
            height: 540
            anchors.centerIn: parent
            radius: 22
            color: "white"
            border.color: "#dce5f0"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 0
                spacing: 0

                Rectangle {
                    Layout.fillHeight: true
                    Layout.preferredWidth: 360
                    radius: 22
                    color: "#173b67"

                    ColumnLayout {
                        anchors.centerIn: parent
                        width: parent.width - 70
                        spacing: 18

                        Label {
                            text: "BANK"
                            color: "#78b7ff"
                            font.pixelSize: 18
                            font.bold: true
                            Layout.alignment: Qt.AlignHCenter
                        }

                        Label {
                            text: "Management System"
                            color: "white"
                            font.pixelSize: 30
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                            Layout.fillWidth: true
                        }

                        Label {
                            color: "#dcecff"
                            wrapMode: Text.WordWrap
                            horizontalAlignment: Text.AlignHCenter
                            Layout.fillWidth: true
                        }
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.margins: 54
                    spacing: 16

                    Label {
                        text: "Welcome back"
                        font.pixelSize: 30
                        font.bold: true
                        color: "#172b4d"
                    }

                    Label {
                        text: "Sign in to continue to your dashboard."
                        color: "#64748b"
                        font.pixelSize: 15
                    }

                    Item { Layout.preferredHeight: 12 }

                    Label { text: "Username"; color: "#334155"; font.bold: true }
                    TextField {
                        id: usernameField
                        Layout.fillWidth: true
                        placeholderText: "Enter username"
                        selectByMouse: true
                        onAccepted: passwordField.forceActiveFocus()
                    }

                    Label { text: "Password"; color: "#334155"; font.bold: true }
                    TextField {
                        id: passwordField
                        Layout.fillWidth: true
                        placeholderText: "Enter password"
                        echoMode: TextInput.Password
                        selectByMouse: true
                        onAccepted: loginButton.clicked()
                    }

                    Label {
                        id: errorLabel
                        Layout.fillWidth: true
                        color: "#dc2626"
                        wrapMode: Text.WordWrap
                        text: backend.lastError
                        visible: text.length > 0
                    }

                    PrimaryButton {
                        id: loginButton
                        Layout.fillWidth: true
                        text: "Sign in"
                        onClicked: backend.login(usernameField.text, passwordField.text)
                    }

                    Label {
                        Layout.fillWidth: true
                        text: "Demo: staff / staff123    customer / customer123"
                        color: "#64748b"
                        font.pixelSize: 11
                        wrapMode: Text.WordWrap
                    }

                    Item { Layout.fillHeight: true }
                }
            }
        }
    }
}
