"""
Mock data for manual testing during development.

Author: Marcin Wojnarski (github.com/mwojnars)
"""


def mock_001():
    samp = [
        'John Smith',
        'Laura Perlman',
        'William C. & Cathy B. Coody',
    ]
    pred = [
        '<GivenName>John</GivenName> <Surname>Smith</Surname>',
        '<GivenName>Laura</GivenName> <Surname>Perlman</Surname>',
        '<GivenName>William</GivenName> <MiddleInitial>C.</MiddleInitial> <And>&</And> <GivenName>Cathy</GivenName> <MiddleInitial>B.</MiddleInitial> <Surname>Coody</Surname>',
    ]
    true = [
        '<GivenName>John</GivenName> <Surname>Smith</Surname>',
        '<GivenName>Laura</GivenName> <Surname>Perlman</Surname>',
        '<GivenName>William</GivenName> <MiddleInitial>C</MiddleInitial> <SuffixOther>&amp;</SuffixOther> <GivenName>Cathy</GivenName> <MiddleInitial>B.</MiddleInitial> <Surname>Coody</Surname>',
    ]
    return true, pred, samp

