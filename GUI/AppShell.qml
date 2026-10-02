import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "components"

Item {
    anchors.fill: parent

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Sidebar {
            Layout.fillHeight: true
            Layout.preferredWidth: 240
            onPageSelected: backend.navigate(page)
            onLogoutRequested: backend.logout()
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#f4f7fb"

            Loader {
                id: pageLoader
                anchors.fill: parent
                anchors.margins: 24
                source: {
                    if (backend.currentPage === "customers") return "CustomerPage.qml"
                    if (backend.currentPage === "accounts") return "AccountsPage.qml"
                    if (backend.currentPage === "transactions") return "TransactionsPage.qml"
                    if (backend.currentPage === "users") return "UsersPage.qml"
                    return "Dashboard.qml"
                }
            }
        }
    }
}
