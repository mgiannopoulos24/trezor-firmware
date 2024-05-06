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

#[cfg(feature = "haptic")]
use crate::trezorhal::haptic::{self, HapticEffect};
use crate::{
    time::Stopwatch,
    ui::{
        component::Label,
        geometry::{Alignment, Point},
    },
};
use pareen;

#[derive(Default, Clone)]
struct HoldToConfirmAnim {
    pub timer: Stopwatch,
}

impl HoldToConfirmAnim {
    const DURATION: f32 = 2.2;

    pub fn is_active(&self) -> bool {
        self.timer.is_running_within(Duration::from(Self::DURATION))
    }

    pub fn eval(&self) -> (f32, f32, f32, f32, Color, f32, f32, f32) {
        let parent_cover_opacity = pareen::constant(0.0).seq_ease_in_out(
            0.0,
            easer::functions::Cubic,
            0.2,
            pareen::constant(1.0),
        );

        let header_opacity = pareen::constant(0.0).seq_ease_out(
            0.1,
            easer::functions::Cubic,
            0.3,
            pareen::constant(1.0),
        );

        let header_opacity2 = pareen::constant(1.0).seq_ease_in(
            2.0,
            easer::functions::Cubic,
            0.2,
            pareen::constant(0.0),
        );

        let circle_opacity = pareen::constant(1.0).seq_ease_out(
            0.1,
            easer::functions::Cubic,
            0.1,
            pareen::constant(0.0),
        );

        let pad_color = pareen::constant(0.0).seq_ease_in_out(
            0.1,
            easer::functions::Cubic,
            1.9,
            pareen::constant(1.0),
        );

        let ciclem_max_height = pareen::constant(0.0).seq_ease_in(
            0.1,
            easer::functions::Cubic,
            1.5,
            pareen::constant(1.0),
        );

        let final_circle_radius = pareen::constant(0.0).seq_ease_in(
            1.6,
            easer::functions::Cubic,
            0.6,
            pareen::constant(1.0),
        );

        let haptic = pareen::constant(0.0).seq_ease_in(
            0.0,
            easer::functions::Linear,
            Self::DURATION,
            pareen::constant(1.0),
        );

        let t = self.timer.elapsed().into();

        let o1 = parent_cover_opacity.eval(t);
        let o2 = header_opacity.eval(t);
        let o3 = circle_opacity.eval(t);
        let o4 = header_opacity2.eval(t);

        let c1 = Color::lerp(
            theme::GREY_EXTRA_DARK,
            Color::rgb(0x09, 0x74, 0x48),
            pad_color.eval(t),
        );

        let h1 = ciclem_max_height.eval(t);
        let r1 = final_circle_radius.eval(t);

        let hap = haptic.eval(t);

        (o1, o2, o3, o4, c1, h1, r1, hap)
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
pub struct HoldToConfirm {
    title: Label<'static>,
    area: Rect,
    button: Button,
    circle_color: Color,
    circle_pad_color: Color,
    circle_inner_color: Color,
    anim: HoldToConfirmAnim,
}

#[derive(Clone)]
enum DismissType {
    Tap,
    Hold,
}

impl HoldToConfirm {
    pub fn new() -> Self {
        let button = Button::new(ButtonContent::Empty)
            .styled(theme::button_default())
            .with_long_press(Duration::from_millis(2200))
            .without_haptics();
        Self {
            title: Label::new(
                "Continue\nHolding".into(),
                Alignment::Start,
                theme::label_title_main(),
            )
            .vertically_centered(),
            area: Rect::zero(),
            circle_color: theme::GREEN,
            circle_pad_color: theme::GREY_EXTRA_DARK,
            circle_inner_color: theme::GREEN_LIGHT,
            button,
            anim: HoldToConfirmAnim::default(),
        }
    }
}

impl Component for HoldToConfirm {
    type Msg = ();

    fn place(&mut self, bounds: Rect) -> Rect {
        self.area = bounds;
        self.button.place(Rect::snap(
            self.area.center(),
            Offset::uniform(120),
            Alignment2D::CENTER,
        ));
        self.title.place(bounds.split_top(42).0);
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
            Some(ButtonMsg::Clicked) => {
                self.anim.reset();
                ctx.request_anim_frame();
                ctx.request_paint();
            }
            Some(ButtonMsg::LongPressed) => {
                #[cfg(feature = "haptic")]
                haptic::play(HapticEffect::HoldToConfirm);
                return Some(());
            }
            _ => (),
        }
        if self.anim.is_active() {
            ctx.request_anim_frame();
            ctx.request_paint();
        }
        None
    }

    fn paint(&mut self) {
        unimplemented!()
    }

    fn render<'s>(&'s self, target: &mut impl Renderer<'s>) {
        let (o1, o2, o3, o4, c1, h1, r1, hap) = self.anim.eval();

        let parent_cover: u8 = u8::lerp(0, 255, o1);
        let title_alpha_start: u8 = u8::lerp(0, 255, o2);
        let title_alpha_end: u8 = u8::lerp(0, 255, o4);
        let circle_alpha: u8 = u8::lerp(0, 255, o3);
        let h1 = i16::lerp(266, 0, h1);
        let r1 = i16::lerp(0, 100, r1);

        shape::Bar::new(self.area)
            .with_fg(theme::BLACK)
            .with_bg(theme::BLACK)
            .with_alpha(parent_cover)
            .render(target);

        let center = self.area.center() + Offset::y(9);

        if parent_cover == 255 {
            shape::Circle::new(center, 88)
                .with_fg(self.circle_inner_color)
                .with_bg(theme::BLACK)
                .with_thickness(2)
                .render(target);

            shape::Bar::new(Rect::new(Point::new(0, 0), Point::new(240, h1)))
                .with_fg(theme::BLACK)
                .with_bg(theme::BLACK)
                .render(target);
        }

        let title_alpha = if title_alpha_end < 255 {
            title_alpha_end
        } else {
            title_alpha_start
        };

        self.title.render_with_alpha(target, title_alpha);

        shape::Circle::new(center, 70)
            .with_fg(c1)
            .with_bg(c1)
            .render(target);
        shape::Circle::new(center, 50)
            .with_fg(self.circle_color)
            .with_bg(self.circle_pad_color)
            .with_thickness(2)
            .with_alpha(circle_alpha)
            .render(target);
        shape::Circle::new(center, 48)
            .with_fg(self.circle_pad_color)
            .with_bg(self.circle_pad_color)
            .with_thickness(8)
            .with_alpha(circle_alpha)
            .render(target);
        shape::Circle::new(center, 40)
            .with_fg(self.circle_inner_color)
            .with_bg(theme::BLACK)
            .with_thickness(2)
            .with_alpha(circle_alpha)
            .render(target);

        shape::ToifImage::new(center, theme::ICON_SIGN.toif)
            .with_fg(theme::GREY_LIGHT)
            .with_alpha(circle_alpha)
            .with_align(Alignment2D::CENTER)
            .render(target);

        if r1 > 0 {
            shape::Circle::new(center, r1)
                .with_fg(theme::BLACK)
                .render(target);
        }

        #[cfg(feature = "haptic")]
        {
            let hap = u8::lerp(0, 20, hap);
            if hap > 0 {
                haptic::play_rtp(hap as i8, 100);
            }
        }
    }
}

#[cfg(feature = "micropython")]
impl crate::ui::flow::Swipable for HoldToConfirm {}

#[cfg(feature = "ui_debug")]
impl crate::trace::Trace for HoldToConfirm {
    fn trace(&self, t: &mut dyn crate::trace::Tracer) {
        t.component("StatusScreen");
        t.child("button", &self.button);
    }
}
