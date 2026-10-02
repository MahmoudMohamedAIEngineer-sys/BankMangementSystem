import QtQuick 2.15
import QtQuick.Controls 2.15

Dialog {
    id: dialog
    property string message: "Are you sure?"
    signal confirmed()
    modal: true
    width: 420
    anchors.centerIn: Overlay.overlay
    title: "Please confirm"

    contentItem: Label {
        text: dialog.message
        wrapMode: Text.WordWrap
        padding: 24
        color: "#334155"
    }

    footer: DialogButtonBox {
        standardButtons: DialogButtonBox.Cancel | DialogButtonBox.Ok
        onAccepted: {
            dialog.confirmed()
            dialog.close()
        }
        onRejected: dialog.close()
    }
}
