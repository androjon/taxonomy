import streamlit as st
import json
from matplotlib import pyplot as plt
from matplotlib_venn import venn2
from wordcloud import WordCloud

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
    taxonomy_text = taxonomy[0:5]
    definition_text = description.split("\n")
    short_definition = definition_text[0]
    rest_of_definition = definition_text[1:]
    #Remove all empty strings from list
    rest_of_definition = [i for i in rest_of_definition if i]
    rest_of_definition = "<br /><br />".join(rest_of_definition)
    return short_definition, rest_of_definition, taxonomy_text

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
            related_groups = st.session_state.occupationdata[id].related_occupation_groups
            skills = st.session_state.skills.get(related_groups[0])
            group = f"<p style='font-size:10px;'>Ordmoln utifrån yrkesgrupp</p>"
            st.markdown(group, unsafe_allow_html=True)
        create_small_wordcloud(skills)

        if taxonomy:    
            taxonomy_text_string = "<br />".join(taxonomy)
            taxonomy_text_string = f"Efterfrågade kompetenser:<br />{taxonomy_text_string}"
            taxonomy_text = f"<p style='font-size:10px;'>{taxonomy_text_string}</p>"
            st.markdown(taxonomy_text, unsafe_allow_html=True)

        rest_of_definition = f"<p style='font-size:10px;'>{rest_of_definition}</p>"
        st.markdown(rest_of_definition, unsafe_allow_html=True)

def show_info_selected(description):
    definition = f"<p style='font-size:10px;'>{description}</p>"
    st.markdown(definition, unsafe_allow_html=True)

def show_initial_information():
    st.logo("af-logotyp-rgb-540px.jpg")
    st.title("Demo")
    initial_text = "Denna demo försöker utforska vad som går att säga utifrån annonsdata, utbildningsbeskrivningar, prognoser och arbetsmarknadstaxonomi. De fyra frågorna den försöker svar på är: 1) VILKA liknande yrken finns det utifrån din yrkes- och utbildningsbakgrund? 2) VARFÖR skulle ett liknande yrke passa just dig? 3) HUR hittar du till annonser för dessa liknande yrken? 4) VAD är bra för dig att lyfta fram i en ansökan till ett liknande yrke? Vill du starta om tryck cmd + r"
    st.markdown(f"<p style='font-size:12px;'>{initial_text}</p>", unsafe_allow_html=True)

def change_state_chosen_background():
    st.session_state.chosen_background = False

def initiate_session_state():
    if "chosen_background" not in st.session_state:
        st.session_state.chosen_background = False
        st.session_state.stored_backgrounds = []
        st.session_state.stored_taxonomy = []
        st.session_state.words_of_experience = []
        st.session_state.words_of_interest = []
        st.session_state.similar_occupations = []

    if len(st.session_state.stored_backgrounds) > 2:
        st.button("Testa om annons- och utbildningsdata kan hjälpa dig att upptäcka dina dolda kompetenser") #on_click = ?

    if st.session_state.chosen_background == True:
        st.button("Lägga till fler yrkes- eller utbildningsbakgrunder", on_click = change_state_chosen_background)

def create_valid_options(input, fields, groups, occupations, titles):
    options_field, options_ssyk_level_4, options_occupations, options_titles = import_options(input)
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
    short_definition, rest_of_definition, taxonomy_text = create_short_rest_of_definition_and_taxonomy_text(id_occupation)
    show_info_selected_sidebar(related_fields_str, related_groups_str, st.session_state.occupationdata[id_occupation].showname, short_definition, rest_of_definition, taxonomy_text, id_occupation)
    
def choose_ssyk_level_4(field_id):
    ssyk_level_4_options = {}
    for g in st.session_state.occupationdata[field_id].related_occupation_groups:
        ssyk_level_4_options[st.session_state.occupationdata[g].showname] = st.session_state.occupationdata[g].id
    valid_ssyk_level_4 = list(ssyk_level_4_options.keys())
    selected_ssyk_level_4 = st.selectbox(
        "Välj en yrkesgrupp",
        (valid_ssyk_level_4), placeholder = "", index = None)
    if selected_ssyk_level_4:
        id_selected_ssyk_level_4 = ssyk_level_4_options.get(selected_ssyk_level_4)
        post_selected_ssyk_level_4(id_selected_ssyk_level_4)

def choose_occupation_name(dict_valid_occupations):
    valid_occupations = list(dict_valid_occupations.keys())
    selected_occupation_name = st.selectbox(
        "Välj en yrkesbenämning",
        (valid_occupations), placeholder = "", index = None)
    if selected_occupation_name:
        id_selected_occupation = dict_valid_occupations.get(selected_occupation_name)
        post_selected_occupation(id_selected_occupation)
        
def choose_occupational_background():
    st.session_state.occupationdata = import_occupationdata()
    st.session_state.definitions = import_data("id_definitions.json")
    st.session_state.taxonomy = import_data("id_taxonomy_wheel.json")
    st.session_state.skills = import_data("ID_skills.json")

    col1, col2 = st.columns(2)

    with col1:
        exclude_fields = st.toggle("inkludera yrkesområden", value = True)
        exclude_groups = st.toggle("inkludera yrkesgrupper", value = False)

    with col2:
        exclude_occupations = st.toggle("inkludera yrkesbenämningar", value = False)
        exclude_titles = st.toggle("inkludera jobbtitlar", value = False)

    valid_options_dict = create_valid_options(st.session_state.occupationdata, exclude_fields, exclude_groups, exclude_occupations, exclude_titles)
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

def choose_background():
    if st.session_state.chosen_background == False:
        occupational_or_educational = st.radio(
                    f"Välj om du vill utgå från en yrkes- eller utbildningsbakgrund",
                    ["yrkesbakgrund", "utbildningsbakgrund"],
                    horizontal = True, index = 0,
            )

    if occupational_or_educational == "yrkesbakgrund":
        choose_occupational_background()

    # if occupational_or_educational == "utbildningsbakgrund":
    #     select_educational_background(masterdata)

def main ():
    show_initial_information()
    initiate_session_state()
    choose_background()

if __name__ == '__main__':
    main ()