import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

Item {
    id: root
    
    required property string downloadName
    required property string downloadUrl
    required property int downloadProgress
    required property string downloadStatus
    required property string downloadSize
    required property int itemIndex
    
    // Add entrance animation with stagger
    opacity: 0
    scale: 0.9
    
    Component.onCompleted: {
        opacityAnimation.start()
        scaleAnimation.start()
    }
    
    PropertyAnimation {
        id: opacityAnimation
        target: root
        property: "opacity"
        from: 0
        to: 1
        duration: 400
        easing.type: Easing.OutCubic
    }
    
    PropertyAnimation {
        id: scaleAnimation
        target: root
        property: "scale"
        from: 0.9
        to: 1
        duration: 400
        easing.type: Easing.OutBack
    }
    
    Rectangle {
        id: cardBackground
        anchors.fill: parent
        color: mouseArea.containsMouse ? Material.color(Material.Grey, Material.Shade800) : Material.color(Material.Grey, Material.Shade900)
        radius: 12
        
        Behavior on color {
            ColorAnimation { duration: 200 }
        }
        
        // Subtle border
        border.color: {
            switch(downloadStatus) {
                case "Completed": return Material.color(Material.Green)
                case "Downloading": return Material.color(Material.Cyan)
                case "Paused": return Material.color(Material.Orange)
                default: return "transparent"
            }
        }
        border.width: 2
        
        Behavior on border.color {
            ColorAnimation { duration: 300 }
        }
    }
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12
        
        // Header with icon and status indicator
        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            
            // File icon
            Rectangle {
                width: 48
                height: 48
                radius: 24
                color: {
                    switch(downloadStatus) {
                        case "Completed": return Material.color(Material.Green, Material.Shade800)
                        case "Downloading": return Material.color(Material.Cyan, Material.Shade800)
                        case "Paused": return Material.color(Material.Orange, Material.Shade800)
                        default: return Material.color(Material.Grey, Material.Shade800)
                    }
                }
                
                Behavior on color {
                    ColorAnimation { duration: 300 }
                }
                
                Label {
                    anchors.centerIn: parent
                    text: "📦"
                    font.pixelSize: 24
                }
                
                // Rotate animation for downloading
                RotationAnimation on rotation {
                    running: downloadStatus === "Downloading"
                    loops: Animation.Infinite
                    from: 0
                    to: 360
                    duration: 3000
                }
            }
            
            Item { Layout.fillWidth: true }
            
            // Status indicator
            Rectangle {
                width: 12
                height: 12
                radius: 6
                color: {
                    switch(downloadStatus) {
                        case "Completed": return Material.color(Material.Green)
                        case "Downloading": return Material.color(Material.Cyan)
                        case "Paused": return Material.color(Material.Orange)
                        case "Pending": return Material.color(Material.Grey)
                        default: return Material.foreground
                    }
                }
                
                Behavior on color {
                    ColorAnimation { duration: 300 }
                }
                
                // Pulse animation for downloading
                SequentialAnimation on scale {
                    running: downloadStatus === "Downloading"
                    loops: Animation.Infinite
                    NumberAnimation { from: 1; to: 1.5; duration: 600 }
                    NumberAnimation { from: 1.5; to: 1; duration: 600 }
                }
            }
        }
        
        // File name
        Label {
            text: downloadName
            font.pixelSize: 15
            font.bold: true
            Layout.fillWidth: true
            wrapMode: Text.Wrap
            maximumLineCount: 2
            elide: Text.ElideRight
            color: Material.foreground
        }
        
        // Progress bar
        ProgressBar {
            Layout.fillWidth: true
            from: 0
            to: 100
            value: downloadProgress
            
            // Smooth progress animation
            Behavior on value {
                NumberAnimation { duration: 500; easing.type: Easing.OutCubic }
            }
            
            // Indeterminate when downloading with 0 progress
            indeterminate: downloadStatus === "Downloading" && downloadProgress === 0
        }
        
        // Progress percentage
        Label {
            text: downloadProgress + "%"
            font.pixelSize: 18
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
            color: Material.accent
        }
        
        Item { Layout.fillHeight: true }
        
        // Status and size info
        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            
            Label {
                text: downloadStatus
                font.pixelSize: 12
                color: Material.color(Material.Grey, Material.Shade400)
                Layout.fillWidth: true
            }
            
            Label {
                text: downloadSize
                font.pixelSize: 12
                font.bold: true
                color: Material.color(Material.Grey, Material.Shade300)
            }
        }
        
        // Action buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            
            Button {
                text: downloadStatus === "Downloading" ? "⏸ Pause" : "▶ Start"
                flat: false
                Material.background: downloadStatus === "Downloading" ? Material.Orange : Material.Green
                Layout.fillWidth: true
                
                onClicked: {
                    if (downloadStatus === "Downloading") {
                        downloadBackend.pauseDownload(itemIndex)
                    } else {
                        downloadBackend.startDownload(itemIndex)
                    }
                }
                
                // Scale animation on press
                scale: pressed ? 0.95 : 1
                Behavior on scale {
                    NumberAnimation { duration: 100 }
                }
            }
            
            Button {
                text: "🗑"
                flat: false
                Material.background: Material.Red
                implicitWidth: 48
                
                onClicked: downloadBackend.removeDownload(itemIndex)
                
                ToolTip.visible: hovered
                ToolTip.text: "Remove"
                
                // Scale animation on press
                scale: pressed ? 0.95 : 1
                Behavior on scale {
                    NumberAnimation { duration: 100 }
                }
            }
        }
    }
}
