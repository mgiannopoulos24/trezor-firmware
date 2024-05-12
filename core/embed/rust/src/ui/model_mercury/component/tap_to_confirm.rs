use crate::{
    time::Duration,
    ui::{
        component::{Component, Event, EventCtx},
        display::Color,
        geometry::{Alignment2D, Offset, Rect},
        lerp::Lerp,
        shape,
        shape::Renderer,
    },
};

use super::{theme, Button, ButtonContent, ButtonMsg};

use crate::{
    time::Stopwatch,
    ui::{component::Label, geometry::Alignment},
};
use pareen;

#[derive(Default, Clone)]
struct TapToConfirmAmin {
    pub timer: Stopwatch,
}

impl TapToConfirmAmin {
    const DURATION: f32 = 0.6;

    pub fn is_active(&self) -> bool {
        self.timer.is_running_within(Duration::from(Self::DURATION))
    }

    pub fn is_finished(&self) -> bool {
        self.timer.elapsed() >= Duration::from(Self::DURATION)
    }

    pub fn eval(&self, final_color: Color) -> (u8, u8, u8, i16, i16, Color) {
        let parent_cover_opacity = pareen::constant(0.0).seq_ease_in_out(
            0.0,
            easer::functions::Cubic,
            0.2,
            pareen::constant(1.0),
        );

        let circle_scale = pareen::constant(0.0).seq_ease_in_out(
            0.0,
            easer::functions::Cubic,
            0.58,
            pareen::constant(1.0),
        );

        let circle_color = pareen::constant(0.0).seq_ease_in_out(
            0.0,
            easer::functions::Cubic,
            0.55,
            pareen::constant(1.0),
        );

        let circle_opacity = pareen::constant(0.0).seq_ease_in_out(
            0.2,
            easer::functions::Cubic,
            0.8,
            pareen::constant(1.0),
        );

        let pad_opacity = pareen::constant(0.0).seq_ease_in_out(
            0.2,
            easer::functions::Cubic,
            0.4,
            pareen::constant(1.0),
        );

        let black_mask_scale = pareen::constant(0.0).seq_ease_in_out(
            0.2,
            easer::functions::Cubic,
            0.8,
            pareen::constant(1.0),
        );

        let t = self.timer.elapsed().into();

        let o1 = parent_cover_opacity.eval(t);
        let o1: u8 = u8::lerp(0, 255, o1);
        let o2 = circle_opacity.eval(t);
        let o2: u8 = u8::lerp(255, 0, o2);
        let o3 = pad_opacity.eval(t);
        let o3: u8 = u8::lerp(255, 0, o3);

        let c1 = Color::lerp(Color::black(), final_color, circle_color.eval(t));

        let s1 = i16::lerp(0, 80, circle_scale.eval(t));
        let s2 = i16::lerp(0, 400, black_mask_scale.eval(t));

        (o1, o2, o3, s1, s2, c1)
    }

    pub fn start(&mut self) {
        self.timer.start();
    }

    pub fn reset(&mut self) {
        self.timer = Stopwatch::new_stopped();
    }
}

/// Component requesting an action from a user. Most typically embedded as a
/// content of a Frame and promptin "Tap to confirm" or "Hold to XYZ".
#[derive(Clone)]
pub struct TapToConfirm {
    area: Rect,
    button: Button,
    circle_color: Color,
    circle_pad_color: Color,
    circle_inner_color: Color,
    mask_color: Color,
    anim: TapToConfirmAmin,
}

#[derive(Clone)]
enum DismissType {
    Tap,
    Hold,
}

impl TapToConfirm {
    pub fn new(
        circle_color: Color,
        circle_inner_color: Color,
        circle_pad_color: Color,
        mask_color: Color,
    ) -> Self {
        let button = Button::new(ButtonContent::Empty)
            .styled(theme::button_default())
            .with_long_press(Duration::from_millis(2200));
        Self {
            area: Rect::zero(),
            circle_color,
            circle_inner_color,
            circle_pad_color,
            mask_color,
            button,
            anim: TapToConfirmAmin::default(),
        }
    }
}

impl Component for TapToConfirm {
    type Msg = ();

    fn place(&mut self, bounds: Rect) -> Rect {
        self.area = bounds;
        self.button.place(Rect::snap(
            self.area.center() + Offset::y(9),
            Offset::uniform(80),
            Alignment2D::CENTER,
        ));
        bounds
    }

    fn event(&mut self, ctx: &mut EventCtx, event: Event) -> Option<Self::Msg> {
        let btn_msg = self.button.event(ctx, event);
        match btn_msg {
            Some(ButtonMsg::Pressed) => {
                self.anim.start();
                ctx.request_anim_frame();
                ctx.request_paint();
            }
            Some(ButtonMsg::Released) => {
                self.anim.reset();
                ctx.request_anim_frame();
                ctx.request_paint();
            }
            Some(ButtonMsg::Clicked) => {}
            _ => (),
        }
        if self.anim.is_active() {
            ctx.request_anim_frame();
            ctx.request_paint();
        }
        if self.anim.is_finished() {
            return Some(());
        };

        None
    }

    fn paint(&mut self) {
        unimplemented!()
    }

    fn render<'s>(&'s self, target: &mut impl Renderer<'s>) {
        let (o1, o2, o3, s1, s2, c1) = self.anim.eval(self.mask_color);

        let center = self.area.center() + Offset::y(9);

        shape::Bar::new(self.area)
            .with_fg(theme::BLACK)
            .with_bg(theme::BLACK)
            .with_alpha(o1)
            .render(target);

        shape::Circle::new(center, 70)
            .with_fg(self.circle_pad_color)
            .with_bg(theme::BLACK)
            .with_thickness(20)
            .with_alpha(o3)
            .render(target);
        shape::Circle::new(center, 50)
            .with_fg(self.circle_color)
            .with_bg(theme::BLACK)
            .with_thickness(2)
            .render(target);
        shape::Circle::new(center, 48)
            .with_fg(self.circle_pad_color)
            .with_bg(theme::BLACK)
            .with_thickness(8)
            .render(target);
        shape::Circle::new(center, s1)
            .with_fg(c1)
            .with_alpha(o2)
            .render(target);
        shape::Circle::new(center, s2)
            .with_fg(theme::BLACK)
            .render(target);

        shape::ToifImage::new(center, theme::ICON_SIMPLE_CHECKMARK.toif)
            .with_fg(theme::GREY_LIGHT)
            .with_alpha(255 - o1)
            .with_align(Alignment2D::CENTER)
            .render(target);
    }
}

#[cfg(feature = "micropython")]
impl crate::ui::flow::Swipable for TapToConfirm {}

#[cfg(feature = "ui_debug")]
impl crate::trace::Trace for TapToConfirm {
    fn trace(&self, t: &mut dyn crate::trace::Tracer) {
        t.component("StatusScreen");
        t.child("button", &self.button);
    }
}
