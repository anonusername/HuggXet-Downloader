import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ApplicationWindow {
    id: rootWindow
    visible: true
    width: 1200
    height: 800
    minimumWidth: 800
    minimumHeight: 600
    title: "HuggXet Downloader - Modern Touch-Enabled Download Manager"
    
    // Material Design styling
    Material.theme: Material.Dark
    Material.accent: Material.Purple
    Material.primary: Material.DeepPurple
    
    // State for view switching
    property bool isListView: true
    
    // Header
    header: ToolBar {
        Material.elevation: 4
        
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 16
            anchors.rightMargin: 16
            spacing: 16
            
            Label {
                text: "🚀 HuggXet Downloader"
                font.pixelSize: 22
                font.bold: true
                Layout.fillWidth: true
                
                // Animated title
                PropertyAnimation on opacity {
                    from: 0
                    to: 1
                    duration: 800
                    running: true
                }
            }
            
            // View toggle buttons
            ToolButton {
                id: listViewBtn
                icon.name: "view-list"
                text: "List"
                checkable: true
                checked: isListView
                onClicked: {
                    isListView = true
                    gridViewBtn.checked = false
                }
                
                ToolTip.visible: hovered
                ToolTip.text: "List View"
            }
            
            ToolButton {
                id: gridViewBtn
                icon.name: "view-grid"
                text: "Grid"
                checkable: true
                checked: !isListView
                onClicked: {
                    isListView = false
                    listViewBtn.checked = false
                }
                
                ToolTip.visible: hovered
                ToolTip.text: "Grid View"
            }
            
            ToolSeparator {}
            
            // Action buttons
            ToolButton {
                text: "▶ Start All"
                Material.foreground: Material.Green
                onClicked: downloadBackend.startAll()
                
                ToolTip.visible: hovered
                ToolTip.text: "Start all downloads"
            }
            
            ToolButton {
                text: "⏸ Pause All"
                Material.foreground: Material.Orange
                onClicked: downloadBackend.pauseAll()
                
                ToolTip.visible: hovered
                ToolTip.text: "Pause all downloads"
            }
            
            ToolButton {
                text: "🗑 Clear"
                Material.foreground: Material.Red
                onClicked: downloadBackend.clearCompleted()
                
                ToolTip.visible: hovered
                ToolTip.text: "Clear completed downloads"
            }
            
            ToolButton {
                text: "➕ Add"
                Material.foreground: Material.Cyan
                onClicked: addDialog.open()
                
                ToolTip.visible: hovered
                ToolTip.text: "Add new download"
            }
        }
    }
    
    // Main content area
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 0
        spacing: 0
        
        // Downloads view container with smooth transitions
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Material.background
            
            // List View
            ListView {
                id: downloadsListView
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12
                clip: true
                visible: isListView
                
                model: downloadBackend.downloadsModel
                
                // Smooth scrolling
                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }
                
                // Add animation for view changes
                opacity: isListView ? 1 : 0
                Behavior on opacity {
                    NumberAnimation { duration: 300 }
                }
                
                delegate: DownloadListDelegate {
                    required property string name
                    required property string url
                    required property int progress
                    required property string status
                    required property string size
                    required property int index
                    
                    width: downloadsListView.width
                    downloadName: name
                    downloadUrl: url
                    downloadProgress: progress
                    downloadStatus: status
                    downloadSize: size
                    itemIndex: index
                }
                
                // Empty state
                Label {
                    anchors.centerIn: parent
                    text: "No downloads yet.\nClick '➕ Add' to get started!"
                    font.pixelSize: 18
                    color: Material.color(Material.Grey)
                    horizontalAlignment: Text.AlignHCenter
                    visible: downloadsListView.count === 0
                }
            }
            
            // Grid View
            GridView {
                id: downloadsGridView
                anchors.fill: parent
                anchors.margins: 16
                cellWidth: 320
                cellHeight: 240
                clip: true
                visible: !isListView
                
                model: downloadBackend.downloadsModel
                
                // Smooth scrolling
                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }
                
                // Add animation for view changes
                opacity: !isListView ? 1 : 0
                Behavior on opacity {
                    NumberAnimation { duration: 300 }
                }
                
                delegate: DownloadGridDelegate {
                    required property string name
                    required property string url
                    required property int progress
                    required property string status
                    required property string size
                    required property int index
                    
                    width: downloadsGridView.cellWidth - 16
                    height: downloadsGridView.cellHeight - 16
                    downloadName: name
                    downloadUrl: url
                    downloadProgress: progress
                    downloadStatus: status
                    downloadSize: size
                    itemIndex: index
                }
                
                // Empty state
                Label {
                    anchors.centerIn: parent
                    text: "No downloads yet.\nClick '➕ Add' to get started!"
                    font.pixelSize: 18
                    color: Material.color(Material.Grey)
                    horizontalAlignment: Text.AlignHCenter
                    visible: downloadsGridView.count === 0
                }
            }
        }
        
        // Status bar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            color: Material.color(Material.Grey, Material.Shade900)
            
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 16
                
                Label {
                    text: "📊 " + downloadsListView.count + " downloads"
                    font.pixelSize: 14
                }
                
                Rectangle {
                    width: 1
                    height: 20
                    color: Material.color(Material.Grey)
                }
                
                Label {
                    text: downloadBackend.statusMessage
                    font.pixelSize: 14
                    Layout.fillWidth: true
                    
                    // Animate status changes
                    PropertyAnimation on opacity {
                        id: statusAnimation
                        from: 0.3
                        to: 1
                        duration: 400
                    }
                    
                    Connections {
                        target: downloadBackend
                        function onStatusMessageChanged() {
                            statusAnimation.restart()
                        }
                    }
                }
            }
        }
    }
    
    // Add Download Dialog
    Dialog {
        id: addDialog
        title: "Add New Download"
        anchors.centerIn: parent
        width: Math.min(500, rootWindow.width - 40)
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
        
        Material.elevation: 8
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 16
            
            Label {
                text: "Enter download details:"
                font.pixelSize: 14
            }
            
            TextField {
                id: nameField
                Layout.fillWidth: true
                placeholderText: "File name (e.g., model-bert.bin)"
                selectByMouse: true
            }
            
            TextField {
                id: urlField
                Layout.fillWidth: true
                placeholderText: "URL (e.g., https://huggingface.co/...)"
                selectByMouse: true
            }
        }
        
        onAccepted: {
            if (nameField.text && urlField.text) {
                downloadBackend.addDownload(nameField.text, urlField.text)
                nameField.text = ""
                urlField.text = ""
            }
        }
        
        onRejected: {
            nameField.text = ""
            urlField.text = ""
        }
        
        // Entrance animation
        enter: Transition {
            NumberAnimation {
                property: "opacity"
                from: 0
                to: 1
                duration: 200
            }
            NumberAnimation {
                property: "scale"
                from: 0.9
                to: 1
                duration: 200
            }
        }
        
        exit: Transition {
            NumberAnimation {
                property: "opacity"
                from: 1
                to: 0
                duration: 150
            }
        }
    }
    
    // Startup animation
    PropertyAnimation {
        target: rootWindow
        property: "opacity"
        from: 0
        to: 1
        duration: 500
        running: true
    }
}
