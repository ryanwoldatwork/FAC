
export function testAuditYearCheckbox(){
    const yearsToCheck = ['all_years','2023','2022','2021','2020','2019','2018','2017','2016'];
    cy.get('#audit-year-2023').uncheck({force: true}).should('not.be.checked');
    //checks all the checkboxes
    cy.get('#audit-year input[type="checkbox"]').each((checkbox, index) => {
        const year = yearsToCheck[index];
        cy.wrap(checkbox).check({ force: true}).should('be.checked').and('have.value',year);
    });
    //unchecks all the checkboxes
    cy.get('#audit-year input[type="checkbox"]').each((checkbox, index) => {
        const year = yearsToCheck[index];
        cy.wrap(checkbox).uncheck({ force: true}).should('not.be.checked').and('have.value',year);
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
    const directFundingCheckbox = ['direct_funding', 'passthrough_funding']
    cy.get('.usa-accordion__button').contains('Direct funding').as('accordionButton').click();
    //checks all the checkboxes
    directFundingCheckbox.forEach((value) => {
        cy.get(`.usa-checkbox__input[value="${value}"]`).check({ force: true }).should('be.checked').and('have.value', value);
    });
    //unchecks all the checkboxes
    directFundingCheckbox.forEach((value) => {
        cy.get(`.usa-checkbox__input[value="${value}"]`).uncheck({ force: true }).should('not.be.checked').and('have.value', value);
    });
    
}

export function testMajorProgram(){
    const majorProgramRadioValues = ['True', 'False']
    cy.get('.usa-accordion__button').contains('Major program').as('accordionButton').click();
    //selects first radio button
    majorProgramRadioValues.forEach((value) => {
        cy.get(`.usa-radio__input[name="major_program"][value="${majorProgramRadioValues[0]}"]`).check({ force: true}).should('be.checked').and('have.value', majorProgramRadioValues[0]);
    });
    //unchecks first radio button by selecting the secone one
    majorProgramRadioValues.forEach((value) => {
        cy.get(`.usa-radio__input[name="major_program"][value="${majorProgramRadioValues[1]}"]`).check({ force: true}).should('be.checked').and('have.value', majorProgramRadioValues[1]);
    });
}