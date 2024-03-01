
//const yearsToCheck = ['2023','2022','2021','2020','2019','2018','2017','2016'];

// export function testSearchSingleReports(){
//     cy.visit('/dissemination/search/');
//     cy.get('#audit-year-All\\ years').check({force: true}).should('be.checked').and('have.value','all_years');
//    // cy.get('#audit-year-2023').uncheck({force: true}).should('not.be.checked');
//     //cy.get('input[type="checkbox"]').check(['2022','2021']);
//     //cy.get('input[type="checkbox"]').each((checkbox, index) => {
//        // const year = yearsToCheck[index];
//        // cy.wrap(checkbox).check({ force: true}).should('have.value',year);
//         //cy.get('#uei-or-ein').clear().type('D7A4J33FUMJ1');
//     //});

//     cy.get('#uei-or-ein').clear().type('D7A4J33FUMJ1');
//     cy.get('#aln').clear().type('93');
//     //cy.get('#entity-name').clear().type('');

//     cy.get('#start-date').type('02/01/2024');
//     cy.get('#end-date').type('02/28/2024');

//     cy.get('#options').select('oversight').should('have.value','oversight');

//     cy.get('#agency-name').type('93');

//     cy.get('#auditee_state').select('VA').should('have.value','VA');

//     cy.get(':nth-child(4) > [type="submit"]').should('have.value','Search').click();
//     cy.url().should('match', /\/dissemination\/search\//);

// }
beforeEach(() => {
    cy.visit('/dissemination/search/');
});

export function testAuditYearCheckbox(){
    const yearsToCheck = ['all_years','2023','2022','2021','2020','2019','2018','2017','2016'];
    cy.get('#audit-year-2023').uncheck({force: true}).should('not.be.checked');
    cy.get('input[type="checkbox"]').each((checkbox, index) => {
        const year = yearsToCheck[index];
        cy.wrap(checkbox).check({ force: true}).should('have.value',year);
    });
}

export function testUEIorEin(){
    cy.get('.usa-accordion__button').contains('UEI or EIN').as('accordionButton').click();
    cy.get('#uei-or-ein').clear().type('D7A4J33FUMJ1');
}

export function testALN(){
    cy.get('.usa-accordion__button').contains('Assistance Listing Number (formerly CFDA').as('accordionButton').click();
    cy.get('#aln').clear().type('93');
}

export function testName(){
    cy.get('.usa-accordion__button').contains('Name (Entity, Auditee, or Auditor)').as('accordionButton').click();
    cy.get('#entity-name').clear().type('Audit McAuditee');

}

export function testFACacceptanceDate(){
    cy.get('.usa-accordion__button').contains('FAC acceptance date').as('accordionButton').click();
    cy.get('#start-date').type('02/01/2024');
    cy.get('#end-date').type('02/29/2024');
}

export function testState(){
    cy.get('.usa-accordion__button').contains('State').as('accordionButton').click();
    cy.get('#auditee_state').select('VA').should('have.value','VA');
}

export function testCogorOver(){
    cy.get('.usa-accordion__button').contains('Cognizant or Oversight').as('accordionButton').click();
    cy.get('#options').select('oversight').should('have.value','oversight');

}

export function testAuditFindings(){
    const auditFindingsCheckbox = ['all_findings', 'is_modified_opinion', 'is_other_findings', 'is_material_weakness', 'is_significant_deficiency', 'is_other_matters', 'is_questioned_costs', 'is_repeat_finding'];
    cy.get('.usa-accordion__button').contains('Audit findings').as('accordionButton').click();
    //checks all the checkboxes
    auditFindingsCheckbox.forEach((value) => {
        cy.get(`.usa-checkbox__input[value="${value}"]`).check({ force: true }).should('be.checked').and('have.value', value);
    });
    //unchecks all the checkboxes
    auditFindingsCheckbox.forEach((value) => {
        cy.get(`.usa-checkbox__input[value="${value}"]`).uncheck({ force: true }).should('not.be.checked').and('have.value', value);
    });
}

export function testDirectFunding(){
    cy.get('.usa-accordion__button').contains('Direct funding').as('accordionButton').click();
}

export function testMajorProgram(){
    cy.get('.usa-accordion__button').contains('Major program').as('accordionButton').click();
}