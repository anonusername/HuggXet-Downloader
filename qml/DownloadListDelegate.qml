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
    
    // Add entrance animation
    opacity: 0
    scale: 0.95
    
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
        duration: 300
        easing.type: Easing.OutCubic
    }
    
    PropertyAnimation {
        id: scaleAnimation
        target: root
        property: "scale"
        from: 0.95
        to: 1
        duration: 300
        easing.type: Easing.OutCubic
    }
    
    Rectangle {
        id: cardBackground
        anchors.fill: parent
        color: mouseArea.containsMouse ? Material.color(Material.Grey, Material.Shade800) : Material.color(Material.Grey, Material.Shade900)
        radius: 8
        
        Behavior on color {
            ColorAnimation { duration: 200 }
        }
        
        layer.enabled: true
        layer.effect: Item {
            Rectangle {
                anchors.fill: parent
                radius: cardBackground.radius
                color: "transparent"
                border.color: "#20FFFFFF"
                border.width: 1
            }
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
        
        // Top row: Name and actions
        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            
            Label {
                text: downloadName
                font.pixelSize: 16
                font.bold: true
                Layout.fillWidth: true
                elide: Text.ElideRight
                
                // Color based on status
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
            }
            
            // Action buttons
            Row {
                spacing: 8
                
                Button {
                    text: downloadStatus === "Downloading" ? "⏸" : "▶"
                    flat: true
                    Material.foreground: downloadStatus === "Downloading" ? Material.Orange : Material.Green
                    implicitWidth: 40
                    implicitHeight: 40
                    
                    onClicked: {
                        if (downloadStatus === "Downloading") {
                            downloadBackend.pauseDownload(itemIndex)
                        } else {
                            downloadBackend.startDownload(itemIndex)
                        }
                    }
                    
                    ToolTip.visible: hovered
                    ToolTip.text: downloadStatus === "Downloading" ? "Pause" : "Start"
                    
                    // Scale animation on press
                    scale: pressed ? 0.9 : 1
                    Behavior on scale {
                        NumberAnimation { duration: 100 }
                    }
                }
                
                Button {
                    text: "🗑"
                    flat: true
                    Material.foreground: Material.Red
                    implicitWidth: 40
                    implicitHeight: 40
                    
                    onClicked: downloadBackend.removeDownload(itemIndex)
                    
                    ToolTip.visible: hovered
                    ToolTip.text: "Remove"
                    
                    // Scale animation on press
                    scale: pressed ? 0.9 : 1
                    Behavior on scale {
                        NumberAnimation { duration: 100 }
                    }
                }
            }
        }
        
        // URL
        Label {
            text: downloadUrl
            font.pixelSize: 12
            Layout.fillWidth: true
            elide: Text.ElideRight
            color: Material.color(Material.Grey, Material.Shade500)
        }
        
        // Progress bar and info row
        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            
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
            
            Label {
                text: downloadProgress + "%"
                font.pixelSize: 14
                font.bold: true
                Layout.minimumWidth: 50
                horizontalAlignment: Text.AlignRight
            }
        }
        
        // Bottom row: Status and size
        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            
            Rectangle {
                width: 8
                height: 8
                radius: 4
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
                SequentialAnimation on opacity {
                    running: downloadStatus === "Downloading"
                    loops: Animation.Infinite
                    NumberAnimation { from: 1; to: 0.3; duration: 800 }
                    NumberAnimation { from: 0.3; to: 1; duration: 800 }
                }
            }
            
            Label {
                text: downloadStatus
                font.pixelSize: 13
                color: Material.color(Material.Grey, Material.Shade400)
            }
            
            Item { Layout.fillWidth: true }
            
            Label {
                text: downloadSize
                font.pixelSize: 13
                font.bold: true
                color: Material.color(Material.Grey, Material.Shade300)
            }
        }
    }
}
