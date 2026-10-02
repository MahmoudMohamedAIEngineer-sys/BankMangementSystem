import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "components"

Item {
    id: page
    property ListModel transactionModel: ListModel {}
    property string pendingSource: ""
    property string pendingDestination: ""
    property string pendingAmount: ""
    property string pendingDescription: ""

    function refresh() {
        var type = typeCombo.currentText === "ALL" ? "" : typeCombo.currentText
        var result = backend.transactions(type, accountFilter.text, searchField.text, dateFilter.text)
        transactionModel.clear()
        if (result) {
            for (var i = 0; i < result.length; i++) transactionModel.append(result[i])
        }
    }

    Component.onCompleted: refresh()
    Connections {
        target: backend
        function onDataChanged() { page.refresh() }
    }

    ConfirmDialog {
        id: transferDialog
        message: "Transfer " + page.pendingAmount + " from " + page.pendingSource + " to " + page.pendingDestination + "?"
        onConfirmed: {
            backend.transfer(page.pendingSource, page.pendingDestination, page.pendingAmount, page.pendingDescription)
            page.refresh()
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 14

        RowLayout {
            Layout.fillWidth: true
            Label {
                text: "Transactions"
                color: "#172b4d"
                font.pixelSize: 30
                font.bold: true
                Layout.fillWidth: true
            }
            ComboBox { id: typeCombo; model: ["ALL", "DEPOSIT", "WITHDRAWAL", "TRANSFER"]; Layout.preferredWidth: 130 }
            TextField { id: accountFilter; placeholderText: "Account"; Layout.preferredWidth: 150 }
            TextField { id: dateFilter; placeholderText: "Date YYYY-MM-DD"; Layout.preferredWidth: 140 }
            TextField { id: searchField; placeholderText: "Search"; Layout.preferredWidth: 150 }
            SecondaryButton { text: "Filter"; onClicked: page.refresh() }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 190
            radius: 14
            color: "white"
            border.color: "#e2e8f0"

            GridLayout {
                anchors.fill: parent
                anchors.margins: 16
                columns: 4
                rowSpacing: 8
                columnSpacing: 10

                Label { text: "Deposit"; font.bold: true; color: "#173b67"; Layout.columnSpan: 4 }
                TextField { id: depositAccount; placeholderText: "Account number"; Layout.fillWidth: true }
                TextField { id: depositAmount; placeholderText: "Amount"; Layout.fillWidth: true }
                TextField { id: depositDescription; placeholderText: "Description"; Layout.fillWidth: true }
                PrimaryButton {
                    text: "Deposit"
                    onClicked: {
                        if (backend.deposit(depositAccount.text, depositAmount.text, depositDescription.text)) {
                            depositAccount.clear(); depositAmount.clear(); depositDescription.clear(); page.refresh()
                        }
                    }
                }

                Label { text: "Withdrawal"; font.bold: true; color: "#173b67"; Layout.columnSpan: 4 }
                TextField { id: withdrawalAccount; placeholderText: "Account number"; Layout.fillWidth: true }
                TextField { id: withdrawalAmount; placeholderText: "Amount"; Layout.fillWidth: true }
                TextField { id: withdrawalDescription; placeholderText: "Description"; Layout.fillWidth: true }
                PrimaryButton {
                    text: "Withdraw"
                    onClicked: {
                        if (backend.withdraw(withdrawalAccount.text, withdrawalAmount.text, withdrawalDescription.text)) {
                            withdrawalAccount.clear(); withdrawalAmount.clear(); withdrawalDescription.clear(); page.refresh()
                        }
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 105
            radius: 14
            color: "white"
            border.color: "#e2e8f0"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 10
                Label { text: "Transfer"; font.bold: true; color: "#173b67" }
                TextField { id: sourceAccount; placeholderText: "From (your account)"; Layout.fillWidth: true }
                TextField { id: destinationAccount; placeholderText: "To (any account number)"; Layout.fillWidth: true }
                TextField { id: transferAmount; placeholderText: "Amount"; Layout.preferredWidth: 110 }
                TextField { id: transferDescription; placeholderText: "Description"; Layout.fillWidth: true }
                PrimaryButton {
                    text: "Transfer"
                    onClicked: {
                        page.pendingSource = sourceAccount.text
                        page.pendingDestination = destinationAccount.text
                        page.pendingAmount = transferAmount.text
                        page.pendingDescription = transferDescription.text
                        transferDialog.open()
                    }
                }
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

                Label { text: "Transaction history"; color: "#172b4d"; font.pixelSize: 18; font.bold: true }

                Rectangle {
                    Layout.fillWidth: true
                    height: 34
                    color: "#eef3f9"
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        Label { text: "Type"; Layout.preferredWidth: 100; font.bold: true; color: "#475569" }
                        Label { text: "Amount"; Layout.preferredWidth: 100; font.bold: true; color: "#475569" }
                        Label { text: "Source"; Layout.preferredWidth: 150; font.bold: true; color: "#475569" }
                        Label { text: "Destination"; Layout.preferredWidth: 150; font.bold: true; color: "#475569" }
                        Label { text: "Performed by"; Layout.preferredWidth: 120; font.bold: true; color: "#475569" }
                        Label { text: "Date"; Layout.fillWidth: true; font.bold: true; color: "#475569" }
                    }
                }

                ListView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    model: transactionModel
                    spacing: 3

                    delegate: Rectangle {
                        width: ListView.view.width
                        height: 46
                        color: index % 2 === 0 ? "#ffffff" : "#f8fafc"
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            Label { text: model.type; Layout.preferredWidth: 100; color: "#173b67"; font.bold: true }
                            Label { text: model.amount; Layout.preferredWidth: 100; color: "#172b4d" }
                            Label { text: model.source; Layout.preferredWidth: 150; color: "#475569" }
                            Label { text: model.destination; Layout.preferredWidth: 150; color: "#475569" }
                            Label { text: model.performedBy; Layout.preferredWidth: 120; color: "#475569" }
                            Label { text: model.createdAt; Layout.fillWidth: true; color: "#64748b" }
                        }
                    }

                    Label {
                        anchors.centerIn: parent
                        visible: transactionModel.count === 0
                        text: "No transactions found"
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
