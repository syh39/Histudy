import pandas as pd
import openpyxl
import numpy as np
from collections import defaultdict

def get_num_people(df_alone_type):
    num_ppl = []
    df_alone_type = df_alone_type.sort_values(['study_with','preference', 'code_1', 'prof_1'], ascending=True).reset_index()
    num_by_code_prof = df_alone_type.groupby(["code_1", "prof_1"]).size().reset_index(name='counts')
    sum = 0
    for index1, row in num_by_code_prof.iterrows():
        num_ppl.append(row['counts'])
        sum = sum + row['counts']
    return num_ppl

def allocate_groups_dict(df_alone, groups, cannot_grouped, num_ppl) :
    idx = 0
    for num in num_ppl :

        if num <= 2 :
            for i in range(0, num):
                value = df_alone.iloc[idx: idx + 1]
                cannot_grouped.add(value['sid'].values[0])
                idx += 1

        else:
            for i in range(0, num):
                value = df_alone.iloc[idx : idx + 1]
                lect = '{}_{}'.format(value['code_1'].values[0], value['prof_1'].values[0])

                if lect not in groups.keys():
                    groups[lect] = set()
                groups[lect].add(value['sid'].values[0])

                idx += 1

def get_num_people_rest(df_alone_type):
    num_ppl = []
    df_alone_type = df_alone_type.sort_values(['code_1'], ascending=True).reset_index()
    num_by_code_prof = df_alone_type.groupby(["code_1"]).size().reset_index(name='counts')
    for index1, row in num_by_code_prof.iterrows():
        num_ppl.append(row['counts'])
    return num_ppl

def allocate_rest_to_other_groups_code(df_grouped_rest, offline_groups, online_groups, anything_groups, hope_col) :
    for index, row in df_grouped_rest.iterrows() :
        status = False
        searching_group = [offline_groups, online_groups, anything_groups]

        for i in range(3):
            if row['preference'] != 3 and i == row['preference'] - 1:
                continue
            for key in searching_group[i].keys():
                if key.rsplit('_', 1)[0] == row[hope_col] :
                    searching_group[i][key].add(row['sid']) 
                    ungrouped[['offline', 'online', 'anything'][row['preference'] - 1]].discard(row['sid'])
                    status = True
                    break
            if status == True : 
                status = False
                break

def automatch(df):
    df = pd.read_csv('Study_Match_Revised.csv', header = 0, index_col = False, names = ['timestamp', 'email', 'id', 'name', 'gender', 'phone', 'preference', 'study_with', 'code_1', 'name_1', 'prof_1', 'code_2', 'name_2', 'prof_2', 'code_3', 'name_3', 'prof_3', 'etc', 'etc_q1', 'etc_q2', 'etc_q3', 'etc_q4', 'agreement'])

    origin_col_name = df.columns
    changed_col_name = ['timestamp', 'email', 'sid', 'name', 'gender', 'phone', 'preference', 'study_with', 'code_1', 'name_1', 'prof_1', 'code_2', 'name_2', 'prof_2', 'code_3', 'name_3', 'prof_3', 'etc', 'etc_q1', 'etc_q2', 'etc_q3', 'etc_q4', 'agreement']

    df = df.set_axis(changed_col_name, axis = 1)
    df.insert(0, 'group', [0 for _ in range(len(df))], True)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.at[df['agreement'] == '아니오', 'group'] = -1
    df = df.drop(df[pd.isnull(df['timestamp'])].index)

    df = df[['group', 'sid', 'gender', 'name', 'email', 'phone', 'timestamp', 'preference', 'study_with', 'code_1', 'prof_1', 'code_2', 'prof_2', 'code_3', 'prof_3']]
    df['preference'] = df['preference'].replace({'대면 스터디로만 매칭' : 1, '비대면 스터디로만 매칭' : 2, '비대면/대면 병행 상관없음' : 3})

    df['prof_1'] = df['prof_1'].str.replace("교수님", "").str.strip()
    df['prof_2'] = df['prof_2'].str.replace("교수님", "").str.strip()
    df['prof_3'] = df['prof_3'].str.replace("교수님", "").str.strip()

    # 과목코드 upper_case + space
    df['code_1'] = df['code_1'].str.upper().str.strip()
    df['code_2'] = df['code_2'].str.upper().str.strip()
    df['code_3'] = df['code_3'].str.upper().str.strip()

    group_num = 1

    # 1. 같이 하는 사람들끼리 먼저 그룹 만들기 (현재 2명만 받았음, 이름이라 애매) => 미완성
    groups_tmp = []
    friend_groups = []
    uncompleted_groups = []
    cannot_grouped_friends = []

    df_friends = df.loc[df['study_with'].notnull()] # + 개인정보 동의한 사람들만
    # df_friends['study_with'] = df_friends['study_with'].str.replace(" *[0-9()]*$", "", regex=True)

    private_groups = list()

    for ind, each in df_friends.iterrows():
        others = {(one[:one.index('(')], one[one.index('(') + 1:one.index(')')]) for one in each['study_with'].split(' ')}
        intersection_check = False
        for private_group in private_groups:
            if len(private_group.intersection(others)) > 0:
                intersection_check = True
                private_group.update(others)
                break
        
        if intersection_check == False:
            private_groups.append(others)


    for private_group in private_groups:
        ready_to_group = True

        # validation check: group members
        if not 3 <= len(private_group) <= 5:
            ready_to_group = False

        else:
            primary_subject = None
            for each in private_group:
                name_query = df[df['name'] == each[0]].index
                phone_query = df[df['phone'].str[-4:] == each[1][-4:]].index

                target = name_query.intersection(phone_query)

                # validation check: member validity
                if len(target) != 1:
                    ready_to_group = False # invalid member
                    break

                # validation check: members except her/himself
                others = {(other[ : other.index('(')], other[other.index('(') + 1 : other.index(')')]) for other in df.at[target[0], 'study_with'].split(' ')}
                if others != private_group.difference({each, }):
                    ready_to_group = False # Unknown member exists
                    break

                # validation check: primary subject
                if primary_subject is None:
                    primary_subject = df.at[target[0], 'code_1']
                elif primary_subject != df.at[target[0], 'code_1']:
                    ready_to_group = False
                    break

        if ready_to_group == False:
            for each in private_group:
                name_query = df[df['name'] == each[0]].index
                phone_query = df[df['phone'].str[-4:] == each[1][-4:]].index

                target = name_query.intersection(phone_query)

                if len(target) != 1:
                    continue

                df.at[target[0], 'group'] = -2
        else:
            for each in private_group:
                name_query = df[df['name'] == each[0]].index
                phone_query = df[df['phone'].str[-4:] == each[1][-4:]].index

                target = name_query.intersection(phone_query)

                if len(target) != 1:
                    continue

                df.at[target[0], 'group'] = group_num
            # df.loc[df['sid'].isin(student_id_lst), 'group'] = group_num
            group_num += 1


    # 2. 이외(혼자 신청한) 사람들한테서 신청 강의, 모임 방식 등 조사
    # df_alone = df.loc[df['study_with'].isnull()]
    df_alone = df.loc[df['group'] == 0]
    # df_alone['preference'] = df_alone['preference'].str.replace("[ ]", "", regex=True)
    # df_alone['code_1'] = df_alone['code_1'].str.replace("[ ]", "", regex=True)


    # # 3. 1지망 과목만 신청한 학생들 먼저 처리하기(대면/비대면 중 하나만 선택한 학생들 먼저, 그 다음에 상관없는 학생들 순으로)

    num_ppl = {'offline' : [], 'online' : [], 'anything' : []}
    grouped = {'offline' : dict(), 'online' : dict(), 'anything' : dict()}
    ungrouped = {'offline' : set(), 'online' : set(), 'anything' : set()}
    preference_type = {1 : 'offline', 2: 'online', 3: 'anything'}

    df_targets = {'offline' : [], 'online' : [], 'anything' : []}

    for preference in preference_type.keys():
        df_targets[preference_type[preference]] = df_alone.loc[df_alone['preference'] == preference]
        df_targets[preference_type[preference]] = df_targets[preference_type[preference]].sort_values(['study_with','preference', 'code_1', 'prof_1'], ascending=True).reset_index()

        num_ppl[preference_type[preference]] = get_num_people(df_targets[preference_type[preference]])
        allocate_groups_dict(df_targets[preference_type[preference]], grouped[preference_type[preference]], ungrouped[preference_type[preference]], num_ppl[preference_type[preference]])

    # 4. 남은 나머지 학생들 처리하기(인원이 부족하여 충원이 필요한 그룹부터 (지망 무시하고) 진행, 이후 지망 순 조합이 가능해질 때 까지 진행하고 나머지는 1지망부터 순서로 처리하기

    num_ppl.update({'offline_rest' : [], 'online_rest' : []})
    grouped.update({'offline_rest' : dict(), 'online_rest' : dict()})
    ungrouped.update({'offline_rest' : set(), 'online_rest' : set()})
    df_targets.update({'offline_rest' : [], 'online_rest' : []})

    for preference in ('offline', 'online'):
        rest = '{}_rest'.format(preference)
        df_targets[rest] = df_alone[df_alone['sid'].isin(ungrouped[preference].union(ungrouped['anything']))]
        df_targets[rest] = df_targets[rest].sort_values(['code_1'], ascending = True).reset_index()

        num_ppl[rest] = get_num_people_rest(df_targets[rest])
        allocate_groups_dict(df_targets[rest], grouped[rest], ungrouped[rest], num_ppl[rest])

        #remove allocated people
        for d in grouped[rest].keys():
            for j in grouped[rest][d]:
                for e in j :
                    if e in ungrouped[preference]:
                        ungrouped[preference].discard(e)
                    if e in ungrouped['anything']:
                        ungrouped['anything'].discard(e)
        
        for lect in grouped[rest].keys():
            if lect not in grouped[preference].keys():
                grouped[preference][lect] = grouped[rest][lect]
            else:
                grouped[preference][lect].update(grouped[rest][lect])

    # allocate rest people to other groups whose # of member is < 5

    df_targets.update({'rest' : []})

    for code in ('code_1', 'code_2', 'code_3'):
        df_targets['rest'] = df_alone[df_alone['sid'].isin(ungrouped['offline'].union(ungrouped['online']).union(ungrouped['anything']))]
        df_targets['rest'] = df_targets['rest'].sort_values([code], ascending = True,).reset_index(drop = True) #reset_index 해야 제대로 작동됨!
        allocate_rest_to_other_groups_code(df_targets['rest'], grouped['offline'], grouped['online'], grouped['anything'], code)

    df_targets['rest'] = df_alone[df_alone['sid'].isin(ungrouped['offline'].union(ungrouped['online']).union(ungrouped['anything']))]
    df_targets['rest'] = df_targets['rest'].sort_values(['code_1', 'prof_1'], ascending = True).reset_index(drop = True)



    # print()
    # print("------ 최종 ------ ")
    # print("offline")
    # sum = 0
    # for e in grouped['offline'].keys(): # rest 랑 합침
    #     sum += len(grouped['offline'][e])
    # print(sum)

    # print("online")
    # sum = 0
    # for e in grouped['online']:  # rest 랑 합침
    #     sum += len(grouped['online'][e])
    # print(sum)

    # sum = 0
    # print("anything")
    # for e in grouped['anything']:
    #     sum += len(grouped['anything'][e])
    # print(sum)


    # print("——할당 안받은 사람——")
    # print(ungrouped['offline'])
    # print(ungrouped['online'])
    # print(ungrouped['anything'])
    # print(len(ungrouped['offline'].union(ungrouped['online']).union(ungrouped['anything'])))
    # print()


    # (option) 5. 3명 그룹 -> 줄이기

    # 6. 인원 수에 맞춰서 그룹 번호 매기기
    # group_num = 1
    for preference in preference_type.values():
        for code, student_id_lst in grouped[preference].items():

            n = len(student_id_lst)

            if n < 11:
                group_numbers = [[3], [4], [5], [3, 3], [4, 3], [4, 4], [5, 4], [5, 5]][n - 3]
            else:
                group_numbers = [[4, 4], [4, 4], [5, 4], [5, 5]][n % 4 - 3] + ([4] * (((n + 1) // 4) - 3)) + ([3] if n % 4 == 3 else [4])

            for sid in student_id_lst:
                df.at[df['sid'] == sid, 'group'] = group_num

                group_numbers[0] -= 1
                if group_numbers[0] == 0:
                    del group_numbers[0]
                    group_num += 1

    # 7. result.csv 파일로 저장
    df = df.sort_values('group', ascending=True).reset_index(drop=True)
    df.to_csv("result.csv",  float_format='%.f', index = False, encoding = 'EUC-KR')