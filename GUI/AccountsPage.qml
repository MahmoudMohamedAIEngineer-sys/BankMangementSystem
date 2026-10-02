import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "components"

Item {
    id: page
    property ListModel accountModel: ListModel {}
    property string pendingCloseAccount: ""

    function refresh() {
        var result = backend.accounts(searchField.text, statusCombo.currentText === "ALL" ? "" : statusCombo.currentText)
        accountModel.clear()
        if (result) {
            for (var i = 0; i < result.length; i++) accountModel.append(result[i])
        }
    }

    Component.onCompleted: refresh()
    Connections {
        target: backend
        function onDataChanged() { page.refresh() }
    }

    ConfirmDialog {
        id: closeDialog
        message: "Close account " + page.pendingCloseAccount + "? The balance must be zero."
        onConfirmed: {
            backend.closeAccount(page.pendingCloseAccount)
            page.refresh()
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 16

        RowLayout {
            Layout.fillWidth: true
            Label {
                text: backend.isStaff ? "Accounts" : "My accounts"
                color: "#172b4d"
                font.pixelSize: 30
                font.bold: true
                Layout.fillWidth: true
            }
            TextField { id: searchField; placeholderText: "Search account"; Layout.preferredWidth: 200 }
            ComboBox { id: statusCombo; model: ["ALL", "ACTIVE", "FROZEN", "CLOSED"]; Layout.preferredWidth: 120 }
            SecondaryButton { text: "Search"; onClicked: page.refresh() }
        }

        Rectangle {
            visible: backend.isStaff
            Layout.fillWidth: true
            Layout.preferredHeight: 105
            radius: 14
            color: "white"
            border.color: "#e2e8f0"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 10
                Label { text: "Create account for customer ID"; color: "#173b67"; font.bold: true }
                TextField { id: customerIdField; placeholderText: "Customer ID"; Layout.preferredWidth: 130; validator: IntValidator { bottom: 1 } }
                ComboBox { id: accountTypeCombo; model: ["SAVINGS", "CURRENT", "BUSINESS"]; Layout.preferredWidth: 130 }
                PrimaryButton {
                    text: "Create account"
                    onClicked: {
                        if (backend.createAccount(parseInt(customerIdField.text), accountTypeCombo.currentText)) {
                            customerIdField.clear(); page.refresh()
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
                spacing: 10

                Label { text: "Account records"; color: "#172b4d"; font.pixelSize: 18; font.bold: true }

                Rectangle {
                    Layout.fillWidth: true
                    height: 34
                    color: "#eef3f9"
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        Label { text: "Account"; Layout.preferredWidth: 150; font.bold: true; color: "#475569" }
                        Label { text: "Customer"; Layout.preferredWidth: 90; font.bold: true; color: "#475569"; visible: backend.isStaff }
                        Label { text: "Type"; Layout.preferredWidth: 100; font.bold: true; color: "#475569" }
                        Label { text: "Balance"; Layout.preferredWidth: 120; font.bold: true; color: "#475569" }
                        Label { text: "Status"; Layout.preferredWidth: 100; font.bold: true; color: "#475569" }
                        Label { text: "Actions"; Layout.fillWidth: true; font.bold: true; color: "#475569" }
                    }
                }

                ListView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    model: accountModel
                    spacing: 4

                    delegate: Rectangle {
                        width: ListView.view.width
                        height: backend.isStaff ? 55 : 48
                        color: index % 2 === 0 ? "#ffffff" : "#f8fafc"

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            Label { text: model.accountNumber; Layout.preferredWidth: 150; color: "#173b67"; font.bold: true }
                            Label { text: model.customerId; Layout.preferredWidth: 90; color: "#475569"; visible: backend.isStaff }
                            Label { text: model.accountType; Layout.preferredWidth: 100; color: "#475569" }
                            Label { text: model.balance; Layout.preferredWidth: 120; color: "#172b4d" }
                            StatusBadge { status: model.status; Layout.preferredWidth: 100 }
                            RowLayout {
                                Layout.fillWidth: true
                                visible: backend.isStaff
                                spacing: 5
                                SecondaryButton { text: "Freeze"; visible: model.status === "ACTIVE"; onClicked: backend.freezeAccount(model.accountNumber) }
                                SecondaryButton { text: "Activate"; visible: model.status === "FROZEN"; onClicked: backend.activateAccount(model.accountNumber) }
                                SecondaryButton {
                                    text: "Close"
                                    visible: model.status !== "CLOSED"
                                    onClicked: { page.pendingCloseAccount = model.accountNumber; closeDialog.open() }
                                }
                            }
                        }
                    }

                    Label {
                        anchors.centerIn: parent
                        visible: accountModel.count === 0
                        text: "No accounts found"
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
