#pragma once
#include <QObject>
#include <QSettings>
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QUrl>

class WolManager : public QObject
{
    Q_OBJECT
public:
    explicit WolManager(QObject* parent = nullptr)
        : QObject(parent), m_nam(new QNetworkAccessManager(this)) {}

    static QString savedUrl()   { QSettings s; return s.value("wol/url").toString(); }
    static QString savedToken() { QSettings s; return s.value("wol/token").toString(); }
    static bool    isEnabled()  { QSettings s; return s.value("wol/enabled", false).toBool(); }

    static void save(const QString& url, const QString& token, bool enabled) {
        QSettings s;
        s.setValue("wol/url",     url);
        s.setValue("wol/token",   token);
        s.setValue("wol/enabled", enabled);
    }

    void wake() {
        if (!isEnabled()) return;
        QString urlStr = savedUrl();
        if (urlStr.isEmpty()) return;
        QNetworkRequest req;
        req.setUrl(QUrl(urlStr));
        req.setRawHeader("Authorization", QByteArray("Bearer ") + savedToken().toUtf8());
        req.setTransferTimeout(5000);
        QNetworkReply* reply = m_nam->get(req);
        connect(reply, &QNetworkReply::finished, reply, &QNetworkReply::deleteLater);
    }

private:
    QNetworkAccessManager* m_nam;
};
