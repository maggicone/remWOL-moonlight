// wolbridge.h - Exposes WolManager to QML as a singleton
// Register in main.cpp with:
//   qmlRegisterSingletonType<WolBridge>("WolBridge", 1, 0, "WolBridge", WolBridge::create);

#pragma once

#include <QObject>
#include <QQmlEngine>
#include <QJSEngine>
#include "wol.h"

class WolBridge : public QObject
{
    Q_OBJECT
    Q_PROPERTY(bool    enabled READ enabled CONSTANT)
    Q_PROPERTY(QString url     READ url     CONSTANT)
    Q_PROPERTY(QString token   READ token   CONSTANT)

public:
    explicit WolBridge(QObject* parent = nullptr)
        : QObject(parent), m_wol(new WolManager(this)) {}

    static QObject* create(QQmlEngine*, QJSEngine*) {
        return new WolBridge();
    }

    bool    enabled() const { return WolManager::isEnabled(); }
    QString url()     const { return WolManager::savedUrl();  }
    QString token()   const { return WolManager::savedToken(); }

    Q_INVOKABLE void save(const QString& url, const QString& token, bool enabled) {
        WolManager::save(url, token, enabled);
    }

    Q_INVOKABLE void wake() {
        m_wol->wake();
    }

private:
    WolManager* m_wol;
};
