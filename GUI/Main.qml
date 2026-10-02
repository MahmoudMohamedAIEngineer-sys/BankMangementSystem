import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    id: window
    visible: true
    width: 1280
    height: 800
    minimumWidth: 1000
    minimumHeight: 650
    title: "Bank Management System"
    color: "#f4f7fb"

    Loader {
        anchors.fill: parent
        source: backend.loggedIn ? "AppShell.qml" : "Login.qml"
    }
}
