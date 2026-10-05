import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, Image, PageBreak, KeepTogether)

FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("F", FD + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("FB", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFontFamily("F", normal="F", bold="FB", italic="F", boldItalic="FB")

NAVY = colors.HexColor("#0B1B3A"); BLUE = colors.HexColor("#1877F2")
TEAL = colors.HexColor("#00B8A9"); LIGHT = colors.HexColor("#F2F5FA")
GREY = colors.HexColor("#5B6577"); LINE = colors.HexColor("#DCE2EC")
W, H = A4; M = 18 * mm

# ---------------- data (hypothetical) ----------------
months = ["Month 1", "Month 2", "Month 3"]
spend = [80000, 100000, 120000]
orders = [134, 272, 442]
aov = 1250
rev = [o * aov for o in orders]
roas = [r / s for r, s in zip(rev, spend)]
cpa = [s / o for s, o in zip(spend, orders)]
T_SPEND, T_REV, T_ORD = sum(spend), sum(rev), sum(orders)
B_ROAS, B_CPA = T_REV / T_SPEND, T_SPEND / T_ORD
inr = lambda x: "₹" + format(int(round(x)), ",")

# ---------------- charts ----------------
fm.fontManager.addfont(FD + "DejaVuSans.ttf")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#B9C2D3", "axes.labelcolor": "#5B6577",
                     "xtick.color": "#5B6577", "ytick.color": "#5B6577"})

def chart1():
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    x = range(3); w = 0.36
    ax.bar([i - w/2 for i in x], [s/1000 for s in spend], w, color="#B9C7E6", label="Ad spend (₹K)")
    ax.bar([i + w/2 for i in x], [r/1000 for r in rev], w, color="#1877F2", label="Revenue (₹K)")
    for i in x:
        ax.text(i - w/2, spend[i]/1000 + 8, f"{spend[i]/1000:.0f}", ha="center", fontsize=8, color="#5B6577")
        ax.text(i + w/2, rev[i]/1000 + 8, f"{rev[i]/1000:.0f}", ha="center", fontsize=8, color="#0B1B3A", weight="bold")
    ax.set_xticks(list(x)); ax.set_xticklabels(months); ax.set_ylim(0, 640)
    ax.yaxis.grid(True, color="#E6EAF2"); ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig("c1.png", dpi=220); plt.close(fig)

def chart2():
    fig, ax = plt.subplots(figsize=(3.5, 2.7))
    ax.plot(months, roas, color="#00B8A9", marker="o", lw=2.5)
    for i, v in enumerate(roas): ax.annotate(f"{v:.2f}x", (i, v), textcoords="offset points", xytext=(0, 8), ha="center", weight="bold", color="#0B1B3A")
    ax.set_ylim(0, 5.6); ax.yaxis.grid(True, color="#E6EAF2"); ax.set_axisbelow(True)
    ax.set_title("ROAS", loc="left", fontsize=10, weight="bold", color="#0B1B3A")
    fig.tight_layout(); fig.savefig("c2.png", dpi=220); plt.close(fig)

def chart3():
    fig, ax = plt.subplots(figsize=(3.5, 2.7))
    ax.bar(months, cpa, color=["#B9C7E6", "#7FA8EE", "#1877F2"], width=0.55)
    for i, v in enumerate(cpa): ax.text(i, v + 12, f"₹{v:.0f}", ha="center", weight="bold", color="#0B1B3A")
    ax.set_ylim(0, 720); ax.yaxis.grid(True, color="#E6EAF2"); ax.set_axisbelow(True)
    ax.set_title("Cost per purchase", loc="left", fontsize=10, weight="bold", color="#0B1B3A")
    fig.tight_layout(); fig.savefig("c3.png", dpi=220); plt.close(fig)

chart1(); chart2(); chart3()

# ---------------- styles ----------------
def S(name, **kw):
    base = dict(fontName="F", fontSize=9.5, leading=14.5, textColor=colors.HexColor("#273247"))
    base.update(kw); return ParagraphStyle(name, **base)
body = S("body"); small = S("small", fontSize=8, leading=11.5, textColor=GREY)
h1 = S("h1", fontName="FB", fontSize=20, leading=25, textColor=NAVY, spaceAfter=4)
h2 = S("h2", fontName="FB", fontSize=12, leading=16, textColor=NAVY, spaceBefore=10, spaceAfter=4)
eyebrow = S("eb", fontName="FB", fontSize=8, leading=11, textColor=BLUE, spaceAfter=2)
bullet = S("bl", leftIndent=12, bulletIndent=0, spaceAfter=3)

def bullets(items): return [Paragraph(i, bullet, bulletText="•") for i in items]

def section(eb, title):
    return [Paragraph(eb.upper(), eyebrow), Paragraph(title, h1)]

def kpi(value, label, sub=None, accent=BLUE):
    v = Paragraph(f'<font name="FB" size="20" color="{accent.hexval().replace("0x","#")}">{value}</font>', S("k", leading=24))
    l = Paragraph(f'<font name="FB" size="8" color="#0B1B3A">{label}</font>', S("kl", leading=11))
    s = Paragraph(sub or "", S("ks", fontSize=7.5, leading=10, textColor=GREY))
    t = Table([[v], [l], [s]], colWidths=[40*mm])
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), LIGHT), ("LINEABOVE", (0,0), (-1,0), 2.5, accent),
                           ("LEFTPADDING", (0,0), (-1,-1), 8), ("TOPPADDING", (0,0), (-1,-1), 2),
                           ("BOTTOMPADDING", (0,2), (-1,2), 8), ("TOPPADDING", (0,0), (-1,0), 9)]))
    return t

def kpi_row(items):
    t = Table([items], colWidths=[43*mm]*4, hAlign="LEFT")
    t.setStyle(TableStyle([("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 3)]))
    return t

def card(title, text_items, accent=BLUE, width=80*mm):
    rows = [[Paragraph(f'<font name="FB" size="10" color="#0B1B3A">{title}</font>', body)]] + [[p] for p in bullets(text_items)]
    t = Table(rows, colWidths=[width])
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), LIGHT), ("LINEBEFORE", (0,0), (0,-1), 3, accent),
                           ("LEFTPADDING", (0,0), (-1,-1), 10), ("RIGHTPADDING", (0,0), (-1,-1), 8),
                           ("TOPPADDING", (0,0), (-1,0), 8), ("BOTTOMPADDING", (0,-1), (-1,-1), 8),
                           ("TOPPADDING", (0,1), (-1,-1), 0), ("BOTTOMPADDING", (0,0), (-1,-2), 0)]))
    return t

# ---------------- page templates ----------------
DISCLAIMER = "Illustrative sample case study. Client name, figures and results are hypothetical and for portfolio demonstration only."

def cover(c, doc):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(BLUE); c.circle(W - 20*mm, H - 30*mm, 70*mm, stroke=0, fill=1)
    c.setFillColor(TEAL); c.circle(W - 5*mm, H - 115*mm, 28*mm, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#122650")); c.rect(0, 0, W, 62*mm, stroke=0, fill=1)
    c.setFillColor(colors.white); c.setFont("FB", 9); c.drawString(M, H - 28*mm, "CASE STUDY  |  META ADS  |  D2C E-COMMERCE")
    c.setFont("FB", 34)
    for i, line in enumerate(["How ₹3 Lakh in", "Meta Ads Drove", "₹10.6 Lakh in", "Revenue in 90 Days"]):
        c.drawString(M, H - 80*mm - i * 15*mm, line)
    c.setFillColor(TEAL); c.rect(M, H - 150*mm, 24*mm, 1.6*mm, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#C9D4EA")); c.setFont("F", 11)
    c.drawString(M, H - 162*mm, "Scaling a skincare brand from 2.1x to 4.6x ROAS")
    c.drawString(M, H - 169*mm, "with a structured creative-testing and funnel system.")
    # bottom stats
    stats = [(f"{B_ROAS:.1f}x", "Blended ROAS"), (inr(B_CPA), "Avg. cost / purchase"), (f"{T_ORD}", "Orders in 3 months")]
    for i, (v, l) in enumerate(stats):
        x = M + i * 58*mm
        c.setFillColor(colors.white); c.setFont("FB", 22); c.drawString(x, 36*mm, v)
        c.setFillColor(colors.HexColor("#9FB0D0")); c.setFont("F", 8.5); c.drawString(x, 30*mm, l)
    c.setFillColor(colors.HexColor("#9FB0D0")); c.setFont("F", 7)
    c.drawString(M, 14*mm, "Prepared by: [Your Name]  |  Performance Marketer, Meta Ads  |  [email]  |  [phone / portfolio link]")
    c.drawString(M, 9.5*mm, DISCLAIMER)
    c.restoreState()

def inner(c, doc):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, H - 10*mm, W, 10*mm, stroke=0, fill=1)
    c.setFillColor(colors.white); c.setFont("FB", 7.5)
    c.drawString(M, H - 6.4*mm, "META ADS CASE STUDY  |  D2C SKINCARE")
    c.setFillColor(TEAL); c.rect(W - M - 18*mm, H - 10*mm, 18*mm, 1.4*mm, stroke=0, fill=1)
    c.setFillColor(GREY); c.setFont("F", 6.8)
    c.drawString(M, 9*mm, DISCLAIMER)
    c.drawRightString(W - M, 9*mm, f"{doc.page}")
    c.setStrokeColor(LINE); c.line(M, 13*mm, W - M, 13*mm)
    c.restoreState()

doc = BaseDocTemplate("Meta_Ads_Case_Study.pdf", pagesize=A4, title="Meta Ads Case Study - D2C Skincare (Illustrative)",
                      author="[Your Name]", leftMargin=M, rightMargin=M, topMargin=20*mm, bottomMargin=20*mm)
fr = Frame(M, 18*mm, W - 2*M, H - 38*mm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="cover", frames=[Frame(0, 0, 1, 1)], onPage=cover, autoNextPageTemplate="inner"),
                      PageTemplate(id="inner", frames=[fr], onPage=inner)])

# ---------------- story ----------------
st = [PageBreak()]

# Page 2: overview
st += section("Overview", "The brand, the problem and the goal")
info = Table([[Paragraph("<b>Client</b>", small), Paragraph("Direct-to-consumer skincare brand (name withheld)", body),
               Paragraph("<b>Duration</b>", small), Paragraph("3 months", body)],
              [Paragraph("<b>Platform</b>", small), Paragraph("Meta Ads (Facebook + Instagram)", body),
               Paragraph("<b>Total ad spend</b>", small), Paragraph("₹3,00,000", body)],
              [Paragraph("<b>Market</b>", small), Paragraph("India, metro and Tier-1 cities", body),
               Paragraph("<b>Avg. order value</b>", small), Paragraph("₹1,250", body)]],
             colWidths=[24*mm, 62*mm, 30*mm, 58*mm])
info.setStyle(TableStyle([("LINEBELOW", (0,0), (-1,-2), 0.5, LINE), ("TOPPADDING", (0,0), (-1,-1), 5),
                          ("BOTTOMPADDING", (0,0), (-1,-1), 5), ("LEFTPADDING", (0,0), (-1,-1), 0)]))
st += [info, Spacer(1, 10)]
st += [kpi_row([kpi("₹10.6L", "Revenue generated", "from ₹3L ad spend", BLUE),
                kpi(f"{B_ROAS:.2f}x", "Blended ROAS", "up from 1.8x baseline", TEAL),
                kpi(inr(B_CPA), "Cost per purchase", "down from ₹620 baseline", BLUE),
                kpi("+230%", "Purchase volume", "Month 3 vs Month 1", TEAL)])]
st += [Paragraph("The challenge", h2),
       Paragraph("The brand had a strong product but inconsistent paid performance. Before we started, "
                 "campaigns were run as a single broad ad set with 2-3 static creatives, no structured testing and "
                 "no separation between prospecting and retargeting. ROAS hovered near 1.8x and cost per purchase "
                 "around ₹620, which was not sustainable at their margins.", body)]
st += [Paragraph("Objectives", h2)]
st += bullets(["Reach a <b>3x+ blended ROAS</b> within 90 days while scaling spend.",
               "Bring cost per purchase <b>below ₹400</b>.",
               "Build a repeatable creative-testing system the brand can keep using."])
st += [Paragraph("What was audited first", h2)]
st += bullets(["Pixel and Conversions API setup (events were duplicated and under-reported).",
               "Audience overlap between campaigns causing internal auction competition.",
               "Creative fatigue: top ad had frequency above 4.5 with falling CTR.",
               "Landing page: slow mobile load and no social proof above the fold."])
st += [PageBreak()]

# Page 3: strategy
st += section("Strategy", "A three-layer funnel built for testing")
st += [Paragraph("Instead of scaling a single campaign, the account was rebuilt around a funnel with clear roles "
                 "for each layer and a weekly creative-testing cadence.", body), Spacer(1, 8)]
funnel = Table([[card("1. Prospecting (TOF)", ["Broad + interest + 1-3% lookalikes", "Advantage+ shopping tested vs manual",
                                              "UGC, founder-story and problem-solution hooks", "~60% of budget"], BLUE, 84*mm),
                 card("2. Warm (MOF)", ["Video viewers 50%+, IG engagers, site visitors 30d", "Testimonial and before/after content",
                                        "Product education carousels", "~20% of budget"], TEAL, 84*mm)],
                [card("3. Retargeting (BOF)", ["ATC + checkout abandoners, 7 and 14 day windows", "Offer-led creatives with urgency",
                                               "Dynamic catalog ads", "~15% of budget"], BLUE, 84*mm),
                 card("4. Testing sandbox", ["Dedicated campaign for new creatives", "Winners promoted to scale campaigns",
                                             "Losers killed within 3-4 days", "~5% of budget"], TEAL, 84*mm)]],
               colWidths=[87*mm, 87*mm])
funnel.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 0),
                            ("TOPPADDING", (0,0), (-1,-1), 0), ("BOTTOMPADDING", (0,0), (-1,-1), 6)]))
st += [funnel]
st += [Paragraph("Creative system", h2)]
st += bullets(["<b>12 to 15 new creatives per month</b> across 4 angles: pain point, social proof, ingredient story, offer.",
               "Hook-first editing: the first 3 seconds tested separately (3-second view rate as the leading metric).",
               "Native-style UGC and creator-shot videos outperformed polished studio ads.",
               "Every ad logged in a testing sheet with hypothesis, result and learning."])
st += [Paragraph("Optimisation rules", h2)]
rules = Table([["Signal", "Action"],
               ["CPA 20% below target for 3 days", "Increase budget by 20% (never more than every 48h)"],
               ["Frequency above 3 on prospecting", "Refresh creatives, expand audience"],
               ["Hook rate under 25%", "Rework first 3 seconds, keep the body"],
               ["Spend above 2x target CPA, no purchase", "Pause the ad, log the learning"]],
              colWidths=[70*mm, 104*mm])
rules.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), NAVY), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                           ("FONTNAME", (0,0), (-1,0), "FB"), ("FONTNAME", (0,1), (-1,-1), "F"), ("FONTSIZE", (0,0), (-1,-1), 8.5),
                           ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT]), ("GRID", (0,0), (-1,-1), 0.4, LINE),
                           ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5), ("LEFTPADDING", (0,0), (-1,-1), 8)]))
st += [rules, PageBreak()]

# Page 4: results
st += section("Results", "Performance across 90 days")
st += [Image("c1.png", width=W - 2*M, height=(W - 2*M) * 3.1 / 7.2), Spacer(1, 4)]
two = Table([[Image("c2.png", width=84*mm, height=84*mm*2.7/3.5), Image("c3.png", width=84*mm, height=84*mm*2.7/3.5)]],
            colWidths=[87*mm, 87*mm])
two.setStyle(TableStyle([("LEFTPADDING", (0,0), (-1,-1), 0)]))
st += [two, Spacer(1, 6)]
rows = [["Metric", "Month 1", "Month 2", "Month 3", "Total / Avg."]]
rows.append(["Ad spend"] + [inr(s) for s in spend] + [inr(T_SPEND)])
rows.append(["Purchases"] + [str(o) for o in orders] + [str(T_ORD)])
rows.append(["Revenue"] + [inr(r) for r in rev] + [inr(T_REV)])
rows.append(["ROAS"] + [f"{r:.2f}x" for r in roas] + [f"{B_ROAS:.2f}x"])
rows.append(["Cost per purchase"] + [inr(c) for c in cpa] + [inr(B_CPA)])
rows.append(["CTR (link)", "0.9%", "1.4%", "1.9%", "1.4%"])
rt = Table(rows, colWidths=[44*mm, 32*mm, 32*mm, 32*mm, 34*mm])
rt.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), NAVY), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                        ("FONTNAME", (0,0), (-1,0), "FB"), ("FONTNAME", (0,1), (-1,-1), "F"), ("FONTNAME", (-1,1), (-1,-1), "FB"),
                        ("FONTSIZE", (0,0), (-1,-1), 8.5), ("ALIGN", (1,0), (-1,-1), "RIGHT"),
                        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT]), ("GRID", (0,0), (-1,-1), 0.4, LINE),
                        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 8)]))
st += [rt, PageBreak()]

# Page 5: learnings + CTA
st += section("Takeaways", "What worked and what we would do next")
st += [Paragraph("Key learnings", h2)]
st += bullets(["<b>Creative was the biggest lever.</b> Three of the top five ads were creator-style UGC; "
               "cost per purchase on these was ~35% lower than studio ads.",
               "<b>Fixing tracking first</b> (Pixel + Conversions API) gave the algorithm cleaner signals and "
               "stabilised delivery within two weeks.",
               "<b>Slow, rule-based scaling</b> (20% steps) let spend grow 50% from Month 1 to Month 3 without ROAS collapsing.",
               "<b>Retargeting was efficient but capped</b> by traffic volume, so prospecting quality drove growth."])
st += [Paragraph("Recommended next steps", h2)]
st += bullets(["Add email/WhatsApp flows to lift repeat purchase rate and LTV.",
               "Test bundles and subscription offers to raise AOV above ₹1,250.",
               "Expand into Tier-2 cities and a second product line with the same testing framework.",
               "Introduce creator whitelisting (partnership ads) for added social proof."])
st += [Spacer(1, 12)]
quote = Table([[Paragraph('<font name="FB" size="22" color="#1877F2">"</font>', body),
                Paragraph("<i>Placeholder for client testimonial. Replace with a real quote if you have one.</i><br/>"
                          '<font size="8" color="#5B6577">[Client name], [Role], [Brand]</font>', S("q", fontSize=10.5, leading=16, textColor=NAVY))]],
              colWidths=[10*mm, 164*mm])
quote.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), LIGHT), ("LINEBEFORE", (0,0), (0,-1), 3, TEAL),
                           ("TOPPADDING", (0,0), (-1,-1), 10), ("BOTTOMPADDING", (0,0), (-1,-1), 10), ("LEFTPADDING", (0,0), (-1,-1), 10)]))
st += [quote, Spacer(1, 16)]
cta = Table([[Paragraph('<font name="FB" size="15" color="#FFFFFF">Want results like these for your brand?</font><br/><br/>'
                        '<font size="9" color="#C9D4EA">Book a free 30-minute ad account audit.<br/>'
                        '[Your Name]  |  [email]  |  [phone]  |  [portfolio / LinkedIn]</font>', S("c", leading=15))]],
            colWidths=[174*mm])
cta.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), NAVY), ("LEFTPADDING", (0,0), (-1,-1), 16),
                         ("TOPPADDING", (0,0), (-1,-1), 16), ("BOTTOMPADDING", (0,0), (-1,-1), 16),
                         ("LINEBELOW", (0,0), (-1,-1), 3, TEAL)]))
st += [cta]

doc.build(st)
print("built")
