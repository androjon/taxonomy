import streamlit as st
import re
import requests
import json
import math
import numpy as np
from matplotlib import pyplot as plt
from matplotlib_venn import venn2
from wordcloud import WordCloud
from collections import Counter
import itertools

from occupation_class import create_occupation_index
from create_options import create_options
from get_descriptions_skills import get_descriptions_skills

@st.cache_data
def import_data(filename):
    with open(filename) as file:
        content = file.read()
    output = json.loads(content)
    return output

@st.cache_data
def import_occupationdata():
    ocupation_data = create_occupation_index()
    return ocupation_data

@st.cache_data
def import_options(input):
    options_field, options_ssyk_level_4, options_occupations, options_titles = create_options(input)
    return options_field, options_ssyk_level_4, options_occupations, options_titles

@st.cache_data
def create_small_wordcloud(skills):
    wordcloud = WordCloud(width = 800, height = 800,
                          background_color = 'white',
                          prefer_horizontal = 1).generate_from_frequencies(skills)
    plt.figure(figsize = (3, 3), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.tight_layout(pad = 0)
    st.pyplot(plt)

@st.cache_data
def create_short_rest_of_definition_and_taxonomy_text(id):
    description, taxonomy = get_descriptions_skills(id)
    taxonomy_wheel = st.session_state.taxonomy.get(id)
    taxonomy.extend(taxonomy_wheel)
    taxonomy = taxonomy[0:20]
    taxonomy_text = taxonomy[0:5]
    definition_text = description.split("\n")
    short_definition = definition_text[0]
    rest_of_definition = definition_text[1:]
    #Remove all empty strings from list
    rest_of_definition = [i for i in rest_of_definition if i]
    rest_of_definition = "<br /><br />".join(rest_of_definition)
    return short_definition, rest_of_definition, taxonomy_text, taxonomy

@st.cache_data
def fetch_number_of_ads(url):
    response = requests.get(url)
    data = response.text
    json_data = json.loads(data)
    data_total = json_data["total"]
    number_of_ads = list(data_total.values())[0]
    return number_of_ads

@st.cache_data
def number_of_ads(ssyk_id, region_id, words):
    ssyk_id = ssyk_id[0]
    base = "https://jobsearch.api.jobtechdev.se/search?"
    end = "&limit=0"
    wordstring = "%20".join(words)
    string_words = "&q=" + wordstring
    if region_id:
        url = base + "occupation-group=" + ssyk_id + "&region=" + region_id + string_words + end
    else:
        url = base + "occupation-group=" + ssyk_id + string_words + end
    number_of_ads = fetch_number_of_ads(url)
    return number_of_ads

@st.cache_data
def add_forecast_addnumbers_occupation(id, id_groups, id_region, arrow_str, words):
    if arrow_str == "små":
        arrow = "\u2193"
    elif arrow_str == "medelstora":
        arrow = "\u2192"
    elif arrow_str == "stora":
        arrow = "\u2191"
    else:
        arrow = ""
    addnumbers = number_of_ads(id_groups, id_region, words)
    name = st.session_state.occupationdata[id].name
    return str(f"{name}({addnumbers}){arrow}"), str(f"{name}({arrow})")


def convert_text(text):
    text = text.strip()
    text = text.lower()
    to_convert = {
        " ": "%20",
        "\^": "%5E",
        "'": "%22"}
    for key, value in to_convert.items():
        text = re.sub(key, value, text)
    return text

def create_link(id_groups, keywords, id_region):
    #Multiple groups in Platsbanken - p=5:5qT8_z9d_8rw;5:J17g_Q2a_2u1
    #There seems to be a 255 character limit for the link and therefore it is difficult to add more than 10 words
    id_groups = id_groups[0]
    base = f"https://arbetsformedlingen.se/platsbanken/annonser?p=5:{id_groups}&q="
    keywords_split = []
    for s in keywords:
        s = convert_text(s)
        keywords_split.append(s)
    keywords_split = "%20".join(keywords_split)
    if id_region:
        region = "&l=2:" + id_region
        return base + keywords_split + region
    else:
        return base + keywords_split

def show_info_selected_sidebar(fields, groups, occupation, short_definition, rest_of_definition, taxonomy, id):
    with st.sidebar:
        SHORT_ELBOW = "└─"
        SPACE_PREFIX = "&nbsp;&nbsp;&nbsp;&nbsp;"
        strings = []
        if fields:
            strings.append(fields)
        if groups:
            group_str = SHORT_ELBOW + groups
            strings.append(group_str)
        if occupation:
            occupations_str = SPACE_PREFIX + SHORT_ELBOW + occupation
            strings.append(occupations_str)
        string = "<br />".join(strings)
        tree = f"<p style='font-size:10px;'>{string}</p>"
        st.markdown(tree, unsafe_allow_html=True)

        short_definition = f"<p style='font-size:10px;'>{short_definition}</p>"
        st.markdown(short_definition, unsafe_allow_html=True)

        skills = st.session_state.skills.get(id)
        if not skills or len(skills) < 20:
            related_group = st.session_state.occupationdata[id].related_occupation_groups[0]
            skills = st.session_state.skills.get(related_group)
            group = f"<p style='font-size:10px;'>Ordmoln utifrån {st.session_state.occupationdata[related_group].name}</p>"
            st.markdown(group, unsafe_allow_html=True)
        create_small_wordcloud(skills)

        if taxonomy:
            taxonomy_text_string = "<br />".join(taxonomy)
            taxonomy_text_string = f"Efterfrågade kompetenser:<br />{taxonomy_text_string}"
            taxonomy_text = f"<p style='font-size:10px;'>{taxonomy_text_string}</p>"
            st.markdown(taxonomy_text, unsafe_allow_html=True)

        rest_of_definition = f"<p style='font-size:10px;'>{rest_of_definition}</p>"
        st.markdown(rest_of_definition, unsafe_allow_html=True)


def show_info_selected_educational_focus_sidebar(name, skills):
    with st.sidebar:
        educational_focus_name = f"<p style='font-size:10px;'>Ordmoln utifrån utbildningsinriktningen {name}</p>"
        st.markdown(educational_focus_name, unsafe_allow_html=True)
        create_small_wordcloud(skills)

def show_info_selected(description):
    definition = f"<p style='font-size:10px;'>{description}</p>"
    st.markdown(definition, unsafe_allow_html=True)


def show_info_similar(short_definition, rest_of_definition, taxonomy, id):
    col1, col2 = st.columns(2)

    with col1:
        skills = st.session_state.skills.get(id)
        if not skills or len(skills) < 20:
                related_group = st.session_state.occupationdata[id].related_occupation_groups[0]
                skills = st.session_state.skills.get(related_group)
                group = f"<p style='font-size:14px;'>Ordmoln utifrån {st.session_state.occupationdata[related_group].name}</p>"
                st.markdown(group, unsafe_allow_html=True)
        if skills:
            occupation = f"<p style='font-size:14px;'>Ordmoln utifrån {st.session_state.occupationdata[id].name}</p>"
            st.markdown(occupation, unsafe_allow_html=True)
        create_small_wordcloud(skills)

    with col2:
        short_definition = f"<p style='font-size:14px;'>{short_definition}</p>"
        st.markdown(short_definition, unsafe_allow_html=True)

        if taxonomy:
            taxonomy_text_string = "<br />".join(taxonomy)
            taxonomy_text_string = f"Efterfrågade kompetenser:<br />{taxonomy_text_string}"
            taxonomy_text = f"<p style='font-size:14px;'>{taxonomy_text_string}</p>"
            st.markdown(taxonomy_text, unsafe_allow_html=True)

        rest_of_definition = f"<p style='font-size:14px;'>{rest_of_definition}</p>"
        st.markdown(rest_of_definition, unsafe_allow_html=True)

def show_initial_information():
    st.logo("af-logotyp-rgb-540px.jpg")
    st.title("Demo")
    initial_text = "Denna demo försöker utforska vad som går att säga utifrån annonsdata, utbildningsbeskrivningar, prognoser och arbetsmarknadstaxonomi. De fyra frågorna den försöker svar på är: 1) VILKA liknande yrken finns det utifrån din yrkes- och utbildningsbakgrund? 2) VARFÖR skulle ett liknande yrke passa just dig? 3) HUR hittar du till annonser för dessa liknande yrken? 4) VAD är bra för dig att lyfta fram i en ansökan till ett liknande yrke? Vill du starta om tryck cmd + r"
    st.markdown(f"<p style='font-size:12px;'>{initial_text}</p>", unsafe_allow_html=True)

def change_state_chosen_background():
    st.session_state.chosen_background = False
    st.session_state.show_more_similar_occupations = False

def change_state_show_more_similar_occupations():
    st.session_state.show_more_similar_occupations = True

def initiate_session_state():
    st.session_state.occupationdata = import_occupationdata()
    st.session_state.definitions = import_data("id_definitions.json")
    st.session_state.taxonomy = import_data("id_taxonomy_wheel.json")
    st.session_state.skills = import_data("ID_skills.json")
    st.session_state.forecasts = import_data("forecast.json")
    st.session_state.regions = import_data("region_name_id.json")
    st.session_state.similar_occupations = import_data("similar_occupations.json")
    st.session_state.similar_ssyk = import_data("similar_ssyk_occupations.json")
    st.session_state.similar_susa = import_data("susa_similar_occupations.json")
    st.session_state.field_of_study_educational_focus = import_data("field_of_study_educational_focus.json")
    st.session_state.field_of_study_educational_focus_skills = import_data("field_of_study_educational_focus_skills.json")

    st.session_state.valid_ids = []
    create_valid_ids()

    if "chosen_background" not in st.session_state:
        st.session_state.chosen_background = False
        st.session_state.show_more_similar_occupations = False
        st.session_state.stored_backgrounds = {}
        st.session_state.stored_background_ssyk = []
        st.session_state.stored_taxonomy = []
        st.session_state.words_of_experience = []
        st.session_state.words_of_interest = []
        st.session_state.shown_similar_occupations = []
        st.session_state.selected_region = ""

def display_saved_data():
    with st.sidebar:
        rubrik = f"<p style='font-size:12px;font-weight: bold;'>Tillfälligt sparad data</p>"
        st.markdown(rubrik, unsafe_allow_html=True)
        bakgrundstext = f"Sparade bakgrunder: {len(st.session_state.stored_backgrounds)}\n"
        bakgrundstext += f"Sparade kompetensbegrepp: {len(st.session_state.stored_taxonomy)}\n"
        bakgrundstext += f"Sparade erfarenhetsord: {len(st.session_state.words_of_experience)}\n"
        bakgrundstext += f"Sparade intresseord: {len(st.session_state.words_of_interest)}"
        text = f"<p style='font-size:12px;white-space: pre;'>{bakgrundstext}</p>"
        st.markdown(text, unsafe_allow_html=True)

def save_selections(id_occupation, level_of_experience, selected_words_of_experience, selected_words_of_interest, selected_words_of_taxonomy, shown_similar_id):
    if id_occupation not in st.session_state.stored_backgrounds:
        st.session_state.chosen_background = True
        st.session_state.stored_backgrounds[id_occupation] = level_of_experience
        related_groups = st.session_state.occupationdata[id_occupation].related_occupation_groups
        for r in related_groups:
            st.session_state.stored_background_ssyk.append(r)

        st.session_state.words_of_experience.extend(selected_words_of_experience)
        st.session_state.words_of_experience = list(set(st.session_state.words_of_experience))

        st.session_state.words_of_interest.extend(selected_words_of_interest)
        st.session_state.words_of_interest = list(set(st.session_state.words_of_interest))

        st.session_state.stored_taxonomy.extend(selected_words_of_taxonomy)
        st.session_state.stored_taxonomy = list(set(st.session_state.stored_taxonomy))

        st.session_state.shown_similar_occupations.extend(shown_similar_id)
        st.session_state.shown_similar_occupations = list(set(st.session_state.shown_similar_occupations))

        display_saved_data()

def save_selections_education(educational_background, level_of_experience, words_of_interest, shown_similar_id):
    if educational_background not in st.session_state.stored_backgrounds:
        st.session_state.chosen_background = True
        st.session_state.stored_backgrounds[educational_background] = level_of_experience

        st.session_state.words_of_interest.extend(words_of_interest)
        st.session_state.words_of_interest = list(set(st.session_state.words_of_interest))

        st.session_state.shown_similar_occupations.extend(shown_similar_id)
        st.session_state.shown_similar_occupations = list(set(st.session_state.shown_similar_occupations))

        display_saved_data()

def create_words_of_interest(selected_skills, similar):
    selected_skills = list(selected_skills.keys())
    selected_skills = selected_skills[0:50]
    similar_skills = {}
    for value in similar.values():
        similar_skills = dict(Counter(similar_skills) + Counter(value))
    words_of_interest = []
    for i in similar_skills:
        if not i in selected_skills:
            words_of_interest.append(i)
    return words_of_interest

def create_keywords(skills, words):
    number_to_save = 10
    listed_skills = list(skills.keys())
    all_skills = words + listed_skills
    keywords = all_skills[0:number_to_save]
    return keywords

def create_similar_data(id, interest):
    similar_ids = st.session_state.similar_occupations.get(id)
    if not similar_ids:
        similar_ids = st.session_state.similar_ssyk.get(st.session_state.occupationdata[id].related_occupation_groups[0])
    similar_within_field_ids = similar_ids["within_field"]
    similar_within_field_ids = [id for id in similar_within_field_ids if id in st.session_state.valid_ids]
    similar_similar_field_ids = similar_ids["similar_field"]
    similar_similar_field_ids = [id for id in similar_similar_field_ids if id in st.session_state.valid_ids]
    if interest == "inte intresserad":
        number_same_area = 0
        number_other_area = 8
    elif interest == "vet inte":
        number_same_area = 4
        number_other_area = 4
    elif interest == "mycket intresserad":
        number_same_area = 8
        number_other_area = 0
    all_similar = {}
    for i in range(number_same_area):
        if i >= len(similar_within_field_ids):
            break
        all_similar[similar_within_field_ids[i]] = st.session_state.skills.get(similar_within_field_ids[i])
    for i in range(number_other_area):
        if i >= len(similar_similar_field_ids):
            break
        all_similar[similar_similar_field_ids[i]] = st.session_state.skills.get(similar_similar_field_ids[i])
    skills_selected = st.session_state.skills.get(id)
    if not skills_selected:
        skills_selected = st.session_state.skills.get(st.session_state.occupationdata[id].related_occupation_groups[0])
    words_of_interest = create_words_of_interest(skills_selected, all_similar)
    return all_similar, words_of_interest

def create_comparable_lists(selected, selected_similar_id, selected_words):
    output = []
    skills_selected = selected[1]
    for s in skills_selected:
        if s in selected_words:
            index_to_move_from = skills_selected.index(s)
            skill_to_move = skills_selected.pop(index_to_move_from)
            skills_selected.insert(0, skill_to_move)
    background = {"name": selected[0],
                "skills": skills_selected}
    output.append(background)
    skills_similar = list(st.session_state.skills.get(selected_similar_id).keys())
    for k in skills_similar:
        if k in selected_words:
            index_to_move_from = skills_similar.index(k)
            skill_to_move = skills_similar.pop(index_to_move_from)
            skills_similar.insert(0, skill_to_move)
    similar = {"name": st.session_state.occupationdata[selected_similar_id].name,
               "skills": skills_similar}
    output.append(similar)
    return output

def count_frequency(data):
    output = {}
    data = Counter(data)
    for k, a in data.items():
        output[k] = a
    return output

def compare_background_and_similar(selected, selected_similar_id, selected_words):
    comparable_list = create_comparable_lists(selected, selected_similar_id, selected_words)
    output = {}
    all_skills = []
    unique_skills = []
    overlapping_skills = []
    for i in comparable_list:
        all_skills = all_skills + i["skills"]
    all_skills = count_frequency(all_skills)
    for k, v in all_skills.items():
        if v == 1:
            unique_skills.append(k)
    for i in comparable_list:
        number_of_unique = 0
        number_added = 0
        number_overlapping = 0
        output[i["name"]] = []
        for s in i["skills"]:
            if s in unique_skills:
                if number_of_unique < 11:
                    if s in selected_words:
                        output[i["name"]].append(f"\u00BB{s}")
                    else:
                        output[i["name"]].append(s)
                    number_added += 1
                    number_of_unique += 1
            else:
                if number_overlapping < 11:
                    overlapping_skills.append(s)
                    number_added += 1
                    number_overlapping += 1
    for i in comparable_list:
        for s in i["skills"]:
            if s in overlapping_skills:
                if s in selected_words:
                    output[i["name"]].append(f"\u00BB{s}")
                else:
                    output[i["name"]].append(s)
    return output

def create_venn(indata):
    titles = []
    skills = []
    for k, v in indata.items():
        if k:
            titles.append(k)
        if v:
            skills.append(set(v))
    plt.figure(figsize= (12, 8))
    venn = venn2(subsets = skills, set_labels = titles, set_colors = ["skyblue", "lightgreen"])
    try:
        venn.get_label_by_id("10").set_text("\n".join(skills[0] - skills[1]))
    except:
        pass
    try:
        venn.get_label_by_id("11").set_text("\n".join(skills[0] & skills[1]))
    except:
        pass
    try:
        venn.get_label_by_id("01").set_text("\n".join(skills[1] - skills[0]))
    except:
        pass
    return plt

def compare_background_similar(selected, id_similar, selected_words_of_experience, selected_words_of_interest):
        valid_similar = {}
        for i in id_similar:
            valid_similar[st.session_state.occupationdata[i].name] = i
        sorted_valid_similar = sorted(list(valid_similar.keys()))
        selected_similar = st.selectbox(
            "Välj ett liknande yrke som du skulle vilja veta mer om",
            (sorted_valid_similar),index = None)

        if selected_similar:
            selected_similar_id = valid_similar.get(selected_similar)
            selected_words = selected_words_of_experience + selected_words_of_interest

            st.write(f"Nedanför ser du likheter och skillnader mellan hur olika arbetsgivare och utbildningsanordnare uttrycker sig när det kommer till kunskaper, erfarenheter och arbetsuppgifter för {selected[0]} och {selected_similar}")

            venn_data = compare_background_and_similar(selected, selected_similar_id, selected_words)

            venn = create_venn(venn_data)
            st.pyplot(venn)

            st.divider()

            short_definition, rest_of_definition, taxonomy_text, taxonomy = create_short_rest_of_definition_and_taxonomy_text(selected_similar_id)
            show_info_similar(short_definition, rest_of_definition, taxonomy[0:5], selected_similar_id)

def show_similar_occupation(selected, selected_region, all_similar, selected_words_of_experience, selected_words_of_interest):

    all_selected_words = selected_words_of_interest + selected_words_of_experience

    st.divider()

    st.write("Nedan finns länkar till annonser för några liknande yrken utifrån tillhörande yrkesgrupp och valda erfarenhets- och intresseord")

    col1, col2 = st.columns(2)

    number_of_similar = 0

    if not selected_region:
        regional_id = None
    else:
        regional_id = st.session_state.regions.get(selected_region)
    for key, value in all_similar.items():
        keywords = create_keywords(value, all_selected_words)
        forecasts = st.session_state.forecasts.get(key)
        if forecasts:
            if regional_id:
                relevant_forecast = forecasts.get(regional_id)
            else:
                relevant_forecast = forecasts.get("i46j_HmG_v64")
            if not relevant_forecast:
                relevant_forecast = ["", "", ""]
            elif not relevant_forecast[0]:
                relevant_forecast[0] = ""
        else:
            relevant_forecast = ["", "", ""]
        related_groups = st.session_state.occupationdata[key].related_occupation_groups
        name_with_addnumbers_forecast,  name_with_forecast = add_forecast_addnumbers_occupation(key, related_groups, regional_id, relevant_forecast[0], keywords)
        link = create_link(related_groups, keywords, regional_id)
        if (number_of_similar % 2) == 0:
            col1.link_button(name_with_addnumbers_forecast, link, help = relevant_forecast[2])
        else:
            col2.link_button(name_with_addnumbers_forecast, link, help = relevant_forecast[2])
        number_of_similar += 1

    compare_background_similar(selected, list(all_similar.keys()), selected_words_of_experience, selected_words_of_interest)

def create_valid_ids():
    options_field, options_ssyk_level_4, options_occupations, options_titles = import_options(st.session_state.occupationdata)
    st.session_state.valid_ids = list(options_occupations.values())

def create_valid_options(fields, groups, occupations, titles):
    options_field, options_ssyk_level_4, options_occupations, options_titles = import_options(st.session_state.occupationdata, )
    output = {}
    if fields:
        output = output | dict(sorted(options_field.items(), key = lambda item: item[0]))
    if groups:
        output = output | dict(sorted(options_ssyk_level_4.items(), key = lambda item: item[0]))
    if occupations:
        output = output | dict(sorted(options_occupations.items(), key = lambda item: item[0]))
    if titles:
        output = output | dict(sorted(options_titles.items(), key = lambda item: item[0]))
    return output

def post_selected_ssyk_level_4(id_ssyk_level_4):
    ssyk_level_4_definition = st.session_state.definitions.get(id_ssyk_level_4)
    show_info_selected(ssyk_level_4_definition)
    occupation_name_options = {}
    for o in st.session_state.occupationdata[id_ssyk_level_4].related_occupation:
        occupation_name_options[st.session_state.occupationdata[o].showname] = st.session_state.occupationdata[o].id
    choose_occupation_name(occupation_name_options)

def post_selected_occupation(id_occupation):
    related_fields = st.session_state.occupationdata[id_occupation].related_occupation_fields
    related_fields_names = []
    for f in related_fields:
        related_fields_names.append(st.session_state.occupationdata[f].showname)
    related_fields_str = "<br />".join(related_fields_names)
    related_groups = st.session_state.occupationdata[id_occupation].related_occupation_groups
    related_groups_names = []
    for g in related_groups:
        related_groups_names.append(st.session_state.occupationdata[g].showname)
    related_groups_str = "<br />".join(related_groups_names)
    short_definition, rest_of_definition, taxonomy_text, taxonomy = create_short_rest_of_definition_and_taxonomy_text(id_occupation)
    show_info_selected_sidebar(related_fields_str, related_groups_str, st.session_state.occupationdata[id_occupation].showname, short_definition, rest_of_definition, taxonomy_text, id_occupation)
    if taxonomy:
        selected_words_of_taxonomy = st.multiselect(
            f"Här är en lista på några viktiga kompetenser för {st.session_state.occupationdata[id_occupation].name}. Välj en eller flera som motsvarar din bakgrund.",
            (taxonomy),)
    else:
        selected_words_of_taxonomy = []

    skills = st.session_state.skills.get(id_occupation)
    if not skills or len(skills) < 20:
        words_of_experience_based_on = f"yrkesgruppen {st.session_state.occupationdata[related_groups[0]].name}"
        skills = st.session_state.skills.get(related_groups[0])
    else:
        words_of_experience_based_on = st.session_state.occupationdata[id_occupation].name
    skills_list = list(skills.keys())
    words_of_experience = skills_list[0:20]

    selected_words_of_experience = st.multiselect(
        f"Här är en lista på några ord från annonser för {words_of_experience_based_on}. Välj ett eller flera ord som beskriver vad du är bra på.",
        (words_of_experience),)

    keywords = create_keywords(skills, selected_words_of_experience)

    col1, col2 = st.columns(2)

    with col2:
        valid_regions = list(st.session_state.regions.keys())
        valid_regions = sorted(valid_regions)

        selected_region = st.selectbox(
            "Begränsa sökområde till ett län",
            (valid_regions), index = None,)

    with col1:
        forecasts = st.session_state.forecasts.get(id_occupation)
        if selected_region:
            regional_id = st.session_state.regions.get(selected_region)
            relevant_forecast = forecasts.get(regional_id)
        else:
            regional_id = None
            relevant_forecast = forecasts.get("i46j_HmG_v64")
        if not relevant_forecast:
            relevant_forecast = ["", "", ""]
        if not relevant_forecast[0]:
            relevant_forecast[0] = ""
        name_with_addnumbers_forecast,  name_with_forecast = add_forecast_addnumbers_occupation(id_occupation, related_groups, regional_id, relevant_forecast[0], keywords)
        link = create_link(related_groups, keywords, regional_id)
        link_name = f"Visa annonser för {name_with_addnumbers_forecast}"
        st.link_button(link_name, link, help = relevant_forecast[2])

        st.button(f"Hjälp med CV för {st.session_state.occupationdata[id_occupation].name}",)

    st.divider()

    selected_level_of_experience = st.radio(
        f"Hur lång erfarenhet har du som {st.session_state.occupationdata[id_occupation].name}?",
        ["kort", "vet inte", "lång"],
        index = 1, horizontal = True,)

    selected_interest_area = st.radio(
        f"Hur intresserad är du av andra yrken inom yrkesområdet {st.session_state.occupationdata[related_fields[0]].name}?",
        ["inte intresserad", "vet inte", "mycket intresserad"],
        index = 1, horizontal = True,)
    
    all_similar, words_of_interest = create_similar_data(id_occupation, selected_interest_area)

    words_of_interest = words_of_interest[0:20]
    selected_words_of_interest = st.multiselect(
        f"Här kommer en lista på några ord från annonser för yrkesbenämningar som på ett eller annat sätt liknar det du tidigare har jobbat med. Välj ett eller flera ord som beskriver vad du är intresserad av.",
        (words_of_interest),)
    
    st.button("Spara bakgrund och börja om från början", on_click = save_selections, args = (id_occupation, selected_level_of_experience, selected_words_of_experience, selected_words_of_interest, selected_words_of_taxonomy, list(all_similar.keys())))

    selected = [st.session_state.occupationdata[id_occupation].name, list(st.session_state.skills.get(id_occupation).keys())]

    show_similar_occupation(selected, selected_region, all_similar, selected_words_of_experience,selected_words_of_interest)

def choose_ssyk_level_4(field_id):
    ssyk_level_4_options = {}
    for g in st.session_state.occupationdata[field_id].related_occupation_groups:
        ssyk_level_4_options[st.session_state.occupationdata[g].showname] = st.session_state.occupationdata[g].id
    valid_ssyk_level_4 = list(ssyk_level_4_options.keys())
    valid_ssyk_level_4 = sorted(valid_ssyk_level_4)
    selected_ssyk_level_4 = st.selectbox(
        "Välj en yrkesgrupp",
        (valid_ssyk_level_4), placeholder = "", index = None)
    if selected_ssyk_level_4:
        id_selected_ssyk_level_4 = ssyk_level_4_options.get(selected_ssyk_level_4)
        post_selected_ssyk_level_4(id_selected_ssyk_level_4)

def choose_occupation_name(dict_valid_occupations):
    valid_occupations = list(dict_valid_occupations.keys())
    valid_occupations = sorted(valid_occupations)
    selected_occupation_name = st.selectbox(
        "Välj en yrkesbenämning",
        (valid_occupations), placeholder = "", index = None)
    if selected_occupation_name:
        id_selected_occupation = dict_valid_occupations.get(selected_occupation_name)
        post_selected_occupation(id_selected_occupation)

def choose_occupational_background():
    col1, col2 = st.columns(2)

    with col1:
        exclude_fields = st.toggle("inkludera yrkesområden", value = True)
        exclude_groups = st.toggle("inkludera yrkesgrupper", value = False)

    with col2:
        exclude_occupations = st.toggle("inkludera yrkesbenämningar", value = False)
        exclude_titles = st.toggle("inkludera jobbtitlar", value = False)

    valid_options_dict = create_valid_options(exclude_fields, exclude_groups, exclude_occupations, exclude_titles)
    valid_options_list = list(valid_options_dict.keys())

    selected_option_occupation_field = st.selectbox(
    "Välj ett yrke/område som du tidigare har arbetat som/inom",
    (valid_options_list), placeholder = "", index = None)

    if selected_option_occupation_field:
        id_selected_option_occupation_field = valid_options_dict.get(selected_option_occupation_field)
        type_selected_option_occupation_field = st.session_state.occupationdata[id_selected_option_occupation_field].type

        if type_selected_option_occupation_field == "yrkesområde":
            field_definition = st.session_state.definitions.get(id_selected_option_occupation_field)
            show_info_selected(field_definition)
            choose_ssyk_level_4(id_selected_option_occupation_field)

        if type_selected_option_occupation_field == "yrkesgrupp":
            post_selected_ssyk_level_4(id_selected_option_occupation_field)

        if type_selected_option_occupation_field == "jobbtitel":
            occupation_name_options = {}
            for o in st.session_state.occupationdata[id_selected_option_occupation_field].related_occupation:
                occupation_name_options[st.session_state.occupationdata[o].showname] = st.session_state.occupationdata[o].id
            choose_occupation_name(occupation_name_options)

        if type_selected_option_occupation_field == "yrkesbenämning":
            post_selected_occupation(id_selected_option_occupation_field)

def choose_educational_background():
    list_field_of_study = sorted(list(st.session_state.field_of_study_educational_focus.keys()))

    selected_field_of_study = st.selectbox(
        "Välj ett område som du har tidigare utbildning inom",
        (list_field_of_study), index = None)
    
    if selected_field_of_study:
        list_educational_focus = sorted(st.session_state.field_of_study_educational_focus.get(selected_field_of_study))

        selected_educational_focus = st.selectbox(
            "Välj en inriktning som du har tidigare utbildning inom",
            (list_educational_focus), index = None)
        
        if selected_educational_focus:
            skills = st.session_state.field_of_study_educational_focus_skills.get(selected_educational_focus)
            if not skills or len(skills) < 20:
                st.write("Ingen tillgänglig data om utbildningsinriktningen")
            else:
                list_skills = list(skills.keys())[0:20]

                show_info_selected_educational_focus_sidebar(selected_educational_focus, skills)

                similar_occupations = st.session_state.similar_susa.get(selected_educational_focus)[0:8]
                similar_occupations_with_names = {}
                all_similar = {}
                for s in similar_occupations:
                    if s in st.session_state.valid_ids:
                       similar_occupations_with_names[st.session_state.occupationdata[s].name] = s
                       all_similar[s] = st.session_state.skills.get(s)

                selected_words_of_experience_education = st.multiselect(
                    f"Välj ett eller flera ord som beskriver vad du har mycket kunskap om.",
                    (list_skills),)
                
                words_of_interest = create_words_of_interest(skills, all_similar)
                words_of_interest = words_of_interest[0:20]
                selected_words_of_interest_education = st.multiselect(
                    f"Här kommer en lista på några ord från annonser för yrkesbenämningar som på ett eller annat sätt liknar det du tidigare har studerat. Välj ett eller flera ord som beskriver vad du är intresserad av.",
                    (words_of_interest),)
                
                col1, col2 = st.columns(2)

                with col1:

                    selected_level_of_experience = st.radio(
                        f"Hur lång utbildning har du inom {selected_educational_focus}?",
                        ["kort", "vet inte", "lång"],
                        index = 1, horizontal = True,)
                    
                with col2:
                    valid_regions = list(st.session_state.regions.keys())
                    valid_regions = sorted(valid_regions)

                    selected_region = st.selectbox(
                        "Begränsa sökområde till ett län",
                        (valid_regions), index = None,)                    

                    st.button("Spara bakgrund och börja om från början", on_click = save_selections_education, args = (selected_educational_focus, selected_level_of_experience, selected_words_of_experience_education, list(similar_occupations_with_names.values())))

                selected = [selected_educational_focus, list(skills.keys())]

                show_similar_occupation(selected, selected_region, all_similar, selected_words_of_experience_education, selected_words_of_interest_education)                

def conconcatenate_stored_background():
    conconatenated_skills = {}
    conconatenated_name = []
    for key, value in st.session_state.stored_backgrounds.items():
        if key in st.session_state.valid_ids:
            background_name = st.session_state.occupationdata[key].name
            bakground_skills = st.session_state.skills.get(key)
            level_of_experience = value
        else:
            background_name = key
            bakground_skills = st.session_state.field_of_study_educational_focus_skills.get(key)
            level_of_experience = value
        conconatenated_name.append(background_name)
        if level_of_experience == "kort":
            experience_faktor = 0.5
        elif level_of_experience == "vet inte":
            experience_faktor = 1
        elif level_of_experience == "lång":
            experience_faktor = 1.5
        skills = {}
        for k, v in bakground_skills.items():
            skills[k] = v * experience_faktor
        conconatenated_skills = dict(Counter(conconatenated_skills) + Counter(skills))
    conconatenated_skills = dict(sorted(conconatenated_skills.items(), key = lambda x:x[1], reverse = True))
    conconatenated_skills = dict(itertools.islice(conconatenated_skills.items(), 100))
    st.session_state.conconcatenate_stored_background = [conconatenated_name, conconatenated_skills]

def norma(data):
    return math.sqrt(sum(x * x for x in data.values()))

def calculate_cosine(A, B):
    keys_in_both = list(A.keys() & B.keys())
    Aa = list(A[k] for k in keys_in_both)
    Bb = list(B[k] for k in keys_in_both)
    cosine = np.dot(Aa, Bb) / (norma(A) * norma(B))
    return round(cosine, 2)

def calculate_more_similar_occupations(skills):
    all_similar = {}
    for key, value in st.session_state.skills.items():
        if key in st.session_state.valid_ids:
            related_groups = st.session_state.occupationdata[key].related_occupation_groups
            check = all(e in related_groups for e in st.session_state.stored_background_ssyk)
            if check == False:
                if key not in st.session_state.shown_similar_occupations:
                    if key not in st.session_state.stored_backgrounds:
                        all_similar[key] = calculate_cosine(skills, value)
    all_similar = dict(sorted(all_similar.items(), key = lambda x:x[1], reverse = True))
    all_similar = dict(itertools.islice(all_similar.items(), 8))    
    return all_similar

def change_word_colour():
    def test_color_func(word, font_size, position, orientation, font_path, random_state):
        if word in st.session_state.words_of_interest:
            return 'blue'
        elif word in st.session_state.words_of_experience:
            return 'green'
        else:
            r, g, b, alpha = plt.get_cmap('cividis')(font_size / 120)
            return (int(r * 255), int(g * 255), int(b * 255))
    return test_color_func

@st.cache_data
def create_wordcloud(skills):
    wordcloud = WordCloud(width = 800, height = 800,
                          background_color = 'white',
                          prefer_horizontal = 1).generate_from_frequencies(skills)
    wordcloud.recolor(color_func = change_word_colour())
    plt.figure(figsize = (6, 6), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.tight_layout(pad = 0)
    st.pyplot(plt)

def show_hidden_competences_and_more_similar_occupations():
    conconcatenate_stored_background()
    new_similar = calculate_more_similar_occupations(st.session_state.conconcatenate_stored_background[1])
    all_similar = {}
    for s in new_similar:
        if s in st.session_state.valid_ids:
            all_similar[s] = st.session_state.skills.get(s)
    with st.sidebar:
        samlad = f"<p style='font-size:10px;'>Din samlade bakgrund</p>"
        st.markdown(samlad, unsafe_allow_html=True)
        create_wordcloud(st.session_state.conconcatenate_stored_background[1])
    conconcatenate_name = "Din samlade bakgrund"
    list_conconcatenate_stored_background = [conconcatenate_name, list(st.session_state.conconcatenate_stored_background[1].keys())]
    show_similar_occupation(list_conconcatenate_stored_background, None, all_similar, st.session_state.words_of_experience, st.session_state.words_of_interest)

def choose_background():
    if "chosen_background" not in st.session_state:
        st.session_state.chosen_background = False
        st.session_state.stored_backgrounds = []
        st.session_state.words_of_experience = []
        st.session_state.words_of_interest = []
        st.session_state.similar_occupations = []
        st.session_state.selected_taxonomy = []

    if len(st.session_state.stored_backgrounds) >= 2:
        st.button("Använd annons- och utbildningsdata för att hitta fler liknande yrken", on_click = change_state_show_more_similar_occupations)
                  
    if st.session_state.show_more_similar_occupations == True:
        show_hidden_competences_and_more_similar_occupations()

    if st.session_state.chosen_background == True:
        st.button("Lägga till fler yrkes- eller utbildningsbakgrunder", on_click = change_state_chosen_background)

    if st.session_state.chosen_background == False and st.session_state.show_more_similar_occupations == False:
        occupational_or_educational = st.radio(
                    f"Välj om du vill utgå från en yrkes- eller utbildningsbakgrund",
                    ["yrkesbakgrund", "utbildningsbakgrund"],
                    horizontal = True, index = 0,
            )

        if occupational_or_educational == "yrkesbakgrund":
            choose_occupational_background()

        if occupational_or_educational == "utbildningsbakgrund":
            choose_educational_background()

def main ():
    initiate_session_state()
    show_initial_information()
    choose_background()

if __name__ == '__main__':
    main ()
