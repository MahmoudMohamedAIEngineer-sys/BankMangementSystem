import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "components"

Item {
    id: page
    property ListModel userModel: ListModel {}
    property int pendingDeactivateUserId: 0

    ConfirmDialog {
        id: deactivateUserDialog
        message: "Deactivate this user? They will no longer be able to log in."
        onConfirmed: backend.deactivateUser(page.pendingDeactivateUserId)
    }

    function refresh() {
        var result = backend.users()
        userModel.clear()
        if (result) {
            for (var i = 0; i < result.length; i++) userModel.append(result[i])
        }
    }

    Component.onCompleted: refresh()
    Connections {
        target: backend
        function onDataChanged() { page.refresh() }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 16

        Label {
            text: "User management"
            color: "#172b4d"
            font.pixelSize: 30
            font.bold: true
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 110
            radius: 14
            color: "white"
            border.color: "#e2e8f0"

            GridLayout {
                anchors.fill: parent
                anchors.margins: 16
                columns: 4
                rowSpacing: 8
                columnSpacing: 10

                Label { text: "Create staff user"; font.bold: true; color: "#173b67"; Layout.columnSpan: 4 }
                TextField { id: staffUsername; placeholderText: "Username"; Layout.fillWidth: true }
                TextField { id: staffPassword; placeholderText: "Password"; echoMode: TextInput.Password; Layout.fillWidth: true }
                PrimaryButton {
                    text: "Create staff"
                    onClicked: {
                        if (backend.createStaff(staffUsername.text, staffPassword.text)) {
                            staffUsername.clear(); staffPassword.clear(); page.refresh()
                        }
                    }
                }
                Item { Layout.fillWidth: true }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 110
            radius: 14
            color: "white"
            border.color: "#e2e8f0"

            GridLayout {
                anchors.fill: parent
                anchors.margins: 16
                columns: 5
                rowSpacing: 8
                columnSpacing: 10

                Label { text: "Create customer login"; font.bold: true; color: "#173b67"; Layout.columnSpan: 5 }
                TextField { id: customerUsername; placeholderText: "Username"; Layout.fillWidth: true }
                TextField { id: customerPassword; placeholderText: "Password"; echoMode: TextInput.Password; Layout.fillWidth: true }
                TextField { id: linkedCustomerId; placeholderText: "Customer ID"; Layout.preferredWidth: 120 }
                PrimaryButton {
                    text: "Create login"
                    onClicked: {
                        if (backend.createCustomerLogin(customerUsername.text, customerPassword.text, parseInt(linkedCustomerId.text))) {
                            customerUsername.clear(); customerPassword.clear(); linkedCustomerId.clear(); page.refresh()
                        }
                    }
                }
                Item { Layout.fillWidth: true }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 14
            color: "white"
            border.color: "#e2e8f0"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 8

                Label { text: "Application users"; color: "#172b4d"; font.pixelSize: 18; font.bold: true }

                Rectangle {
                    Layout.fillWidth: true
                    height: 34
                    color: "#eef3f9"
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        Label { text: "Username"; Layout.fillWidth: true; font.bold: true; color: "#475569" }
                        Label { text: "Role"; Layout.preferredWidth: 110; font.bold: true; color: "#475569" }
                        Label { text: "Customer ID"; Layout.preferredWidth: 100; font.bold: true; color: "#475569" }
                        Label { text: "Status"; Layout.preferredWidth: 90; font.bold: true; color: "#475569" }
                        Label { text: ""; Layout.preferredWidth: 110 }
                    }
                }

                ListView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    model: userModel
                    spacing: 4

                    delegate: Rectangle {
                        width: ListView.view.width
                        height: 48
                        color: index % 2 === 0 ? "#ffffff" : "#f8fafc"
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            Label { text: model.username; Layout.fillWidth: true; color: "#173b67"; font.bold: true }
                            Label { text: model.role; Layout.preferredWidth: 110; color: "#475569" }
                            Label { text: model.customerId === "" ? "—" : model.customerId; Layout.preferredWidth: 100; color: "#475569" }
                            Label {
                                text: model.status
                                Layout.preferredWidth: 90
                                color: model.isActive ? "#166534" : "#991b1b"
                                font.bold: true
                            }
                            SecondaryButton {
                                text: "Deactivate"
                                visible: model.isActive
                                Layout.preferredWidth: 100
                                onClicked: {
                                    page.pendingDeactivateUserId = model.id
                                    deactivateUserDialog.open()
                                }
                            }
                            SecondaryButton {
                                text: "Activate"
                                visible: !model.isActive
                                Layout.preferredWidth: 100
                                onClicked: backend.activateUser(model.id)
                            }
                        }
                    }

                    Label {
                        anchors.centerIn: parent
                        visible: userModel.count === 0
                        text: "No users found"
                        color: "#94a3b8"
                    }
                }
            }
        }

        Label {
            Layout.fillWidth: true
            text: backend.lastError || backend.lastSuccess
            color: backend.lastError ? "#b91c1c" : "#166534"
            visible: text.length > 0
        }
    }
}
