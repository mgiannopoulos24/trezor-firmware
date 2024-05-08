use crate::ui::{
    component::{Component, Event, EventCtx},
    geometry::Rect,
    model_mercury::theme,
    shape::Renderer,
};

use super::{HoldToConfirm, TapToConfirm};

/// Component requesting an action from a user. Most typically embedded as a
/// content of a Frame and promptin "Tap to confirm" or "Hold to XYZ".
#[derive(Clone)]
pub struct PromptScreen {
    area: Rect,
    tap_to_confirm: Option<TapToConfirm>,
    hold_to_confirm: Option<HoldToConfirm>,
}

impl PromptScreen {
    pub fn new_hold_to_confirm() -> Self {
        Self {
            area: Rect::zero(),
            tap_to_confirm: None,
            hold_to_confirm: Some(HoldToConfirm::new()),
        }
    }

    pub fn new_tap_to_confirm() -> Self {
        Self {
            area: Rect::zero(),
            tap_to_confirm: Some(TapToConfirm::new(
                theme::GREEN,
                theme::GREEN,
                theme::GREY_EXTRA_DARK,
            )),
            hold_to_confirm: None,
        }
    }

    pub fn new_tap_to_cancel() -> Self {
        Self {
            area: Rect::zero(),
            tap_to_confirm: Some(TapToConfirm::new(
                theme::ORANGE_LIGHT,
                theme::ORANGE_LIGHT,
                theme::GREY_EXTRA_DARK,
            )),
            hold_to_confirm: None,
        }
    }
}

impl Component for PromptScreen {
    type Msg = ();

    fn place(&mut self, bounds: Rect) -> Rect {
        self.area = bounds;
        if let Some(hold_to_confirm) = &mut self.hold_to_confirm {
            hold_to_confirm.place(self.area);
        }
        if let Some(tap_to_confirm) = &mut self.tap_to_confirm {
            tap_to_confirm.place(self.area);
        }
        bounds
    }

    fn event(&mut self, ctx: &mut EventCtx, event: Event) -> Option<Self::Msg> {
        if let Some(hold_to_confirm) = &mut self.hold_to_confirm {
            if let Some(()) = hold_to_confirm.event(ctx, event) {
                return Some(());
            }
        }
        if let Some(tap_to_confirm) = &mut self.tap_to_confirm {
            if let Some(()) = tap_to_confirm.event(ctx, event) {
                return Some(());
            }
        }

        None
    }

    fn paint(&mut self) {
        todo!()
    }

    fn render<'s>(&'s self, target: &mut impl Renderer<'s>) {
        if let Some(hold_to_confirm) = &self.hold_to_confirm {
            hold_to_confirm.render(target);
        }
        if let Some(tap_to_confirm) = &self.tap_to_confirm {
            tap_to_confirm.render(target);
        }
    }
}

#[cfg(feature = "micropython")]
impl crate::ui::flow::Swipable for PromptScreen {}

#[cfg(feature = "ui_debug")]
impl crate::trace::Trace for PromptScreen {
    fn trace(&self, t: &mut dyn crate::trace::Tracer) {
        t.component("StatusScreen");
        if let Some(hold_to_confirm) = &self.hold_to_confirm {
            t.child("hold_to_confirm", hold_to_confirm);
        }
        if let Some(tap_to_confirm) = &self.tap_to_confirm {
            t.child("tap_to_confirm", tap_to_confirm);
        }
    }
}
