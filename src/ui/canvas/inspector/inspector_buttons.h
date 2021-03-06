#ifndef INSPECTOR_BUTTONS_H
#define INSPECTOR_BUTTONS_H

#include <QPointer>

#include "ui/util/button.h"

class ScriptDatum;
class NodeInspector;

class InspectorScriptButton : public GraphicsButton
{
    Q_OBJECT
public:
    InspectorScriptButton(ScriptDatum* s, QGraphicsItem* parent);
    QRectF boundingRect() const override;
    void paint(QPainter* painter, const QStyleOptionGraphicsItem* option,
               QWidget* widget=0) override;
protected slots:
    void onPressed();
protected:
    QPointer<ScriptDatum> script;
};

class InspectorShowHiddenButton : public GraphicsButton
{
    Q_OBJECT
public:
    InspectorShowHiddenButton(QGraphicsItem* parent,
                              NodeInspector* inspector);
    QRectF boundingRect() const override;
    void paint(QPainter* painter, const QStyleOptionGraphicsItem* option,
               QWidget* widget=0) override;
protected slots:
    void onPressed();
protected:
    bool toggled;
    NodeInspector* inspector;
};
#endif
