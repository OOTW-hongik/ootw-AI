def get_clothclass(top5_labels, category):
    if category == 'outer':
        cloth_class = 'outer_etc'
        for i in top5_labels:
            if i in ['Outwear', 'Blazer', 'Hoodie']:
                cloth_class = i
                break
    elif category == 'top':
        cloth_class = 'top_etc'
        for i in top5_labels:
            if i in ['T-Shirt', 'Shirt', 'Top', 'Dress', 'Body', 'Longsleeve', 'Undershirt', 'Polo', 'Blouse', 'Hoodie']:
                cloth_class = i
                break
    elif category == 'bottom':
        cloth_class = 'bottom_etc'
        for i in top5_labels:
            if i in ['Pants', 'Shorts', 'Skirt']:
                cloth_class = i
                break
    elif category == 'etc':
        return '기타'

    cloth_dict = {'Not sure': '불확실', 'T-Shirt': '반팔티', 'Shoes': '신발', 'Shorts': '반바지',
                    'Shirt': '셔츠', 'Pants': '긴바지', 'Skirt': '스커트', 'Other': '불확실', 'Top': '민소매티',
                    'Outwear': '자켓', 'Dress': '원피스', 'Body': '원피스', 'Longsleeve': '긴팔티', 
                    'Undershirt': '민소매티', 'Hat': '모자', 'Polo': '카라티', 'Blouse': '블라우스', 
                    'Hoodie': '후드티', 'Skip': '불확실', 'Blazer': '블레이저', 'outer_etc': '기타 아우터',
                    'top_etc' : '기타 상의', 'bottom_etc' : '기타 하의'}

    cloth_class = cloth_dict[cloth_class]
    if cloth_class == '후드티' and category == 'outer':
        cloth_class = '후드집업'

    return cloth_class
