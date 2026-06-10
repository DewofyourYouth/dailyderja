<%*
// Obsidian Templater script for "نسمة كلمة" (Word Breeze / Word of the Day)
const wordAr = await tp.system.prompt("Arabic Word (e.g. ضعيف)");
const wordEn = await tp.system.prompt("English Meaning (e.g. weak)");
const translit = await tp.system.prompt("Transliteration (e.g. da3if)");
const ipa = await tp.system.prompt("IPA Shami (e.g. dˤaˈʕiːf)");
const root = await tp.system.prompt("Root (e.g. ض · ع · ف)");
const pos = await tp.system.prompt("Part of Speech (e.g. adjective)");
const mnemonic = await tp.system.prompt("Mnemonic (e.g. You DIE IF you're weak.)");
const audioFile = await tp.system.prompt("Audio Filename (e.g. daif.mp3)", translit.replace(/[^a-zA-Z0-9]/g, '') + ".mp3");
const seriesOrder = await tp.system.prompt("Series Order (Check site for next number)");

const date = tp.date.now("YYYY-MM-DDTHH:mm:ssZ");
const slug = wordEn.toLowerCase().replace(/ /g, "-");
const title = `${wordAr} (${wordEn}) — Shami Arabic Word of the Day`;
const summary = `Learn the word for '${wordEn}' in Shami Arabic (${wordAr}) with examples and mnemonic.`;
const description = `Explore the Shami Arabic word '${wordAr}' meaning ${wordEn}. Includes audio examples, IPA, and usage notes.`;

// Rename file to index.md and move to correct folder logic would go here in Obsidian
// For now, this just generates the content
-%>
---
title: "<% title %>"
summary: "<% summary %>"
description: "<% description %>"
date: "<% date %>"
image: featured.jpg
tags:
  - shami-arabic
  - vocabulary
  - adjectives
  - arabic-word
  - ipa
  - example-sentences
categories:
  - language-learning
draft: false
learn: true
dialects:
  - shami
series:
  - نسمة كلمة
series_order: <% seriesOrder %>
postLang: ar
cssclasses:
  - arabic-note
---


{{< word ar="<% wordAr %>" sh_ipa="<% ipa %>" tn_ipa="<% ipa %>" meaning="<% wordEn %>" root="<% root %>" pos="<% pos %>" audio="/audio/<% audioFile %>" note="Add usage notes here." >}}

{{< recall ar="<% wordAr %>" translit="<% translit %>" meaning="<% wordEn %>" mnemonic="<% mnemonic %>" note="Add recall note here." audio="/audio/<% audioFile %>" image="<% slug %>-flashcard.jpg" imageAlt="The Daily Derja flashcard for <% wordAr %>, <% wordEn %>" >}}



{{< join-channels >}}

## أمثلة

{{% examples title="Usage" titleAr="الاستخدام" %}}
{{< example ar="الكلمة في جملة هون." en="The word in a sentence here." tag="masc." ipa="" audio="/audio/example-1.mp3" >}}
{{< example ar="الكلمة في جملة تانية." en="The word in another sentence." tag="fem." ipa="" audio="/audio/example-2.mp3" >}}
{{% /examples %}}

---
{{< ltr >}}
*I post something short here most days while learning Arabic. If this helped, you’ll probably like the next one too.*
{{</ ltr >}}
