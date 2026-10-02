import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "components"

Item {
    id: page
    property ListModel customerModel: ListModel {}

    function refresh() {
        var result = backend.customers(searchField.text)
        customerModel.clear()
        if (result) {
            for (var i = 0; i < result.length; i++) customerModel.append(result[i])
        }
    }

    Component.onCompleted: refresh()
    Connections {
        target: backend
        function onDataChanged() { page.refresh() }
    }

    property int editingCustomerId: 0

    Dialog {
        id: editDialog
        title: "Edit customer"
        modal: true
        width: 430
        anchors.centerIn: Overlay.overlay
        standardButtons: Dialog.Ok | Dialog.Cancel

        contentItem: ColumnLayout {
            spacing: 10
            TextField { id: editName;    placeholderText: "Name";    Layout.fillWidth: true }
            TextField { id: editPhone;   placeholderText: "Phone";   Layout.fillWidth: true }
            TextField { id: editEmail;   placeholderText: "Email";   Layout.fillWidth: true }
            TextField { id: editAddress; placeholderText: "Address"; Layout.fillWidth: true }
        }

        onAccepted: {
            if (backend.updateCustomer(editingCustomerId, editName.text, editPhone.text, editEmail.text, editAddress.text))
                page.refresh()
        }
    }

    function openEditor(item) {
        editingCustomerId = item.id
        editName.text    = item.name
        editPhone.text   = item.phone
        editEmail.text   = item.email
        editAddress.text = item.address
        editDialog.open()
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 16

        RowLayout {
            Layout.fillWidth: true
            Label {
                text: "Customers"
                color: "#172b4d"
                font.pixelSize: 30
                font.bold: true
                Layout.fillWidth: true
            }
            TextField {
                id: searchField
                placeholderText: "Search customers"
                Layout.preferredWidth: 240
                onAccepted: page.refresh()
            }
            SecondaryButton {
                text: "Search"
                onClicked: page.refresh()
            }
        }

        // ── Add customer form ─────────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 110
            radius: 14
            color: "white"
            border.color: "#e2e8f0"

            GridLayout {
                anchors.fill: parent
                anchors.margins: 16
                columns: 6
                columnSpacing: 10
                rowSpacing: 8

                Label {
                    text: "Add customer"
                    font.bold: true
                    color: "#173b67"
                    Layout.columnSpan: 6
                }

                // Row 1 — customer details
                TextField { id: nameField;    placeholderText: "Full name";  Layout.fillWidth: true }
                TextField { id: phoneField;   placeholderText: "Phone";      Layout.fillWidth: true }
                TextField { id: emailField;   placeholderText: "Email";      Layout.fillWidth: true }
                TextField { id: addressField; placeholderText: "Address";    Layout.fillWidth: true }
                PrimaryButton {
                    text: "Add customer"
                    Layout.columnSpan: 2
                    Layout.fillWidth: true
                    onClicked: {
                        if (backend.createCustomer(
                                nameField.text, phoneField.text, emailField.text, addressField.text)) {
                            nameField.clear()
                            phoneField.clear()
                            emailField.clear()
                            addressField.clear()
                            page.refresh()
                        }
                    }
                }
            }
        }

        // ── Customer records table ────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 14
            color: "white"
            border.color: "#e2e8f0"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 10

                RowLayout {
                    Layout.fillWidth: true
                    Label { text: "Customer records"; font.pixelSize: 18; font.bold: true; color: "#172b4d"; Layout.fillWidth: true }
                    Label { text: customerModel.count + " records"; color: "#64748b" }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 34
                    color: "#eef3f9"
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        Label { text: "ID";     Layout.preferredWidth: 45;  font.bold: true; color: "#475569" }
                        Label { text: "Name";   Layout.fillWidth: true;     font.bold: true; color: "#475569" }
                        Label { text: "Phone";  Layout.preferredWidth: 150; font.bold: true; color: "#475569" }
                        Label { text: "Email";  Layout.preferredWidth: 220; font.bold: true; color: "#475569" }
                        Label { text: "Status"; Layout.preferredWidth: 90;  font.bold: true; color: "#475569" }
                        Label { text: "";       Layout.preferredWidth: 170 }
                    }
                }

                ListView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    model: customerModel
                    spacing: 4

                    delegate: Rectangle {
                        width: ListView.view.width
                        height: 48
                        color: index % 2 === 0 ? "#ffffff" : "#f8fafc"

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            Label { text: model.id;     Layout.preferredWidth: 45;  color: "#334155" }
                            Label { text: model.name;   Layout.fillWidth: true;     color: "#172b4d"; elide: Text.ElideRight }
                            Label { text: model.phone;  Layout.preferredWidth: 150; color: "#475569" }
                            Label { text: model.email;  Layout.preferredWidth: 220; color: "#475569"; elide: Text.ElideRight }
                            Label {
                                text: model.status
                                Layout.preferredWidth: 90
                                color: model.isActive ? "#166534" : "#991b1b"
                                font.bold: true
                            }
                            RowLayout {
                                Layout.preferredWidth: 170
                                spacing: 5
                                SecondaryButton {
                                    text: "Edit"
                                    Layout.preferredWidth: 70
                                    onClicked: page.openEditor(model)
                                }
                                SecondaryButton {
                                    visible: model.isActive
                                    text: "Deactivate"
                                    Layout.preferredWidth: 95
                                    onClicked: backend.deactivateCustomer(model.id)
                                }
                                SecondaryButton {
                                    visible: !model.isActive
                                    text: "Activate"
                                    Layout.preferredWidth: 95
                                    onClicked: backend.activateCustomer(model.id)
                                }
                            }
                        }
                    }

                    Label {
                        anchors.centerIn: parent
                        visible: customerModel.count === 0
                        text: "No customers found"
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
