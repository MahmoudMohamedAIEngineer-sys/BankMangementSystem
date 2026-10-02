import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "components"

Item {
    id: page
    property var dashboard: ({})
    property ListModel recentModel: ListModel {}
    property ListModel accountModel: ListModel {}

    function refresh() {
        var result = backend.dashboardData()
        if (!result) return
        dashboard = result
        recentModel.clear()
        accountModel.clear()
        if (result.recentTransactions) {
            for (var i = 0; i < result.recentTransactions.length; i++)
                recentModel.append(result.recentTransactions[i])
        }
        if (result.accounts) {
            for (var j = 0; j < result.accounts.length; j++)
                accountModel.append(result.accounts[j])
        }
    }

    Component.onCompleted: refresh()

    Connections {
        target: backend
        function onDataChanged() { page.refresh() }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 18

        RowLayout {
            Layout.fillWidth: true

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                Label {
                    text: backend.isStaff ? "System dashboard" : "My dashboard"
                    color: "#172b4d"
                    font.pixelSize: 30
                    font.bold: true
                }
                Label {
                    text: backend.isStaff
                          ? "Overview of the bank's current activity"
                          : "Welcome back, " + (dashboard.customerName || backend.username)
                    color: "#64748b"
                    font.pixelSize: 15
                }
            }

            Label {
                text: dashboard.role || ""
                color: "#173b67"
                font.bold: true
                font.pixelSize: 13
            }
        }

        GridLayout {
            columns: 4
            Layout.fillWidth: true
            columnSpacing: 14
            rowSpacing: 14

            StatCard {
                Layout.fillWidth: true
                title: backend.isStaff ? "Active customers" : "My accounts"
                value: backend.isStaff ? String(dashboard.activeCustomers || 0) : String(dashboard.totalAccounts || 0)
                accent: "#2563eb"
            }
            StatCard {
                Layout.fillWidth: true
                title: backend.isStaff ? "Active accounts" : "Active accounts"
                value: String(dashboard.activeAccounts || 0)
                accent: "#0f766e"
            }
            StatCard {
                Layout.fillWidth: true
                title: backend.isStaff ? "Total balance" : "My balance"
                value: dashboard.totalBalance || "$0.00"
                accent: "#7c3aed"
            }
            StatCard {
                Layout.fillWidth: true
                title: backend.isStaff ? "Transactions" : "Recent activity"
                value: backend.isStaff ? String(dashboard.totalTransactions || 0) : String(recentModel.count)
                accent: "#d97706"
            }

            StatCard {
                Layout.fillWidth: true
                visible: backend.isStaff
                title: "Total deposits"
                value: dashboard.totalDeposits || "$0.00"
                accent: "#166534"
            }
            StatCard {
                Layout.fillWidth: true
                visible: backend.isStaff
                title: "Total withdrawals"
                value: dashboard.totalWithdrawals || "$0.00"
                accent: "#991b1b"
            }
            StatCard {
                Layout.fillWidth: true
                visible: backend.isStaff
                title: "Total transfers"
                value: dashboard.totalTransfers || "$0.00"
                accent: "#1d4ed8"
            }
            Item { Layout.fillWidth: true; visible: backend.isStaff }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 18

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: 14
                color: "white"
                border.color: "#e2e8f0"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 12

                    Label {
                        text: backend.isStaff ? "Recent transactions" : "My recent transactions"
                        color: "#172b4d"
                        font.pixelSize: 18
                        font.bold: true
                    }

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: recentModel
                        spacing: 8

                        delegate: Rectangle {
                            width: ListView.view.width
                            height: 58
                            radius: 8
                            color: index % 2 === 0 ? "#f8fafc" : "white"

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 12

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 2
                                    Label {
                                        text: model.type + "  •  " + model.amount
                                        color: "#172b4d"
                                        font.bold: true
                                    }
                                    Label {
                                        text: model.description || "No description"
                                        color: "#64748b"
                                        font.pixelSize: 12
                                        elide: Text.ElideRight
                                        Layout.fillWidth: true
                                    }
                                }

                                Label {
                                    text: model.createdAt
                                    color: "#64748b"
                                    font.pixelSize: 11
                                }
                            }
                        }

                        Label {
                            anchors.centerIn: parent
                            visible: recentModel.count === 0
                            text: "No transactions yet"
                            color: "#94a3b8"
                        }
                    }
                }
            }

            Rectangle {
                Layout.preferredWidth: 340
                Layout.fillHeight: true
                radius: 14
                color: "white"
                border.color: "#e2e8f0"
                visible: !backend.isStaff

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 12

                    Label {
                        text: "My accounts"
                        color: "#172b4d"
                        font.pixelSize: 18
                        font.bold: true
                    }

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: accountModel
                        spacing: 8

                        delegate: Rectangle {
                            width: ListView.view.width
                            height: 76
                            radius: 9
                            color: "#f8fafc"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 5
                                Label {
                                    text: model.accountNumber
                                    color: "#173b67"
                                    font.bold: true
                                }
                                Label {
                                    text: model.accountType + "  •  " + model.balance
                                    color: "#334155"
                                }
                                StatusBadge {
                                    status: model.status
                                }
                            }
                        }
                    }
                }
            }
        }

        Label {
            Layout.fillWidth: true
            text: backend.lastError || backend.lastSuccess
            color: backend.lastError ? "#b91c1c" : "#166534"
            visible: text.length > 0
            wrapMode: Text.WordWrap
        }
    }
}
