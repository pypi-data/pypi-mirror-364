from playwright.sync_api import Playwright, sync_playwright, expect
from ConfigAutomation.Baseline.src.utils import *


def configure(playwright: Playwright, rowcount, datadict, videodir) -> dict:
    browser, context, page = OpenBrowser(playwright, False, videodir)
    page.goto(BASEURL)

    # Login to application
    page.wait_for_timeout(5000)
    if page.get_by_placeholder("User ID").is_visible():
        page.get_by_placeholder("User ID").click()
        page.get_by_placeholder("User ID").fill(IMPLUSRID)
        page.get_by_placeholder("Password").fill(IMPLUSRPWD)
    else:
        page.get_by_placeholder("User name").click()
        page.get_by_placeholder("User name").fill(IMPLUSRID)
        page.get_by_role("textbox", name="Password").fill(IMPLUSRPWD)
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(5000)

    # Navigate to Setup and Maintenance
    page.locator("//a[@title=\"Settings and Actions\"]").click()
    page.get_by_role("link", name="Setup and Maintenance").click()
    page.wait_for_timeout(40000)
    page.get_by_role("link", name="Tasks").click()

    # Entering respective option in global Search field and searching
    page.locator("[id=\"__af_Z_window\"]").get_by_role("link", name="Search").click()
    page.wait_for_timeout(3000)
    page.get_by_role("textbox").click()
    page.get_by_role("textbox").type("Elements")
    page.get_by_role("textbox").press("Enter")
    page.wait_for_timeout(2000)
    page.get_by_role("link", name="Elements", exact=True).click()


    i = 0
    while i < rowcount:
        datadictvalue = datadict[i]
        page.wait_for_timeout(10000)
        if page.locator("//a[text()='View']//following::div[@role='button'][1]").is_visible():
           page.locator("//a[text()='View']//following::div[@role='button'][1]").click()
        page.get_by_role("link", name="Create").click()
        page.locator("[id=\"__af_Z_window\"]").get_by_role("combobox", name="Legislative Data Group").click()
        page.wait_for_timeout(5000)
        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_LGSLTV_DATA_GROUP"], exact=True).click()
        page.wait_for_timeout(2000)
        page.get_by_role("combobox", name="Primary Classification").click()
        page.wait_for_timeout(3000)
        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRMRY_CLSSFCTN"]).click()
        page.wait_for_timeout(2000)


        # Secondary Classification as Expense Reimbursement
        if datadictvalue["C_SCNDRY_CLSSFCTN"]=='Expense Reimbursement':
            page.get_by_role("combobox", name="Secondary Classification").click()
            page.wait_for_timeout(3000)
            page.get_by_text(datadictvalue["C_SCNDRY_CLSSFCTN"], exact=True).click()
            page.wait_for_timeout(2000)
            if datadictvalue["C_CTGRY"]=='Standard':
                page.get_by_role("combobox", name="Category").click()
                page.wait_for_timeout(3000)
                page.get_by_text(datadictvalue["C_CTGRY"], exact=True).click()
                page.get_by_role("button", name="Continue").click()
                page.wait_for_timeout(3000)

                # Entering Basic Details
                page.get_by_label("Name", exact=True).type(datadictvalue["C_ELMNT_NAME"])
                page.get_by_label("Reporting Name").type(datadictvalue["C_RPRTNG_NAME"])
                page.get_by_label("Description").type(datadictvalue["C_DSCRPTN"])
                page.locator("//label[text()='Effective Date']//following::input[1]").clear()
                page.locator("//label[text()='Effective Date']//following::input[1]").type(datadictvalue["C_EFCTV_DATE"])


                # Selecting Currency
                page.get_by_role("combobox", name="Input Currency").click()
                page.wait_for_timeout(2000)
                page.get_by_text(datadictvalue["C_INPUT_CRNCY"],exact=True).click()

                # Selecting Duration
                ### Should every person eligible for the element automatically receive it?
                if datadictvalue["C_ATMTC_ELMNT_ELGBLTY"] != 'N/A':
                    if datadictvalue["C_ATMTC_ELMNT_ELGBLTY"] == 'Yes':
                        page.locator("// label[text() = 'Should every person eligible for the element automatically receive it?'] // following::label[text() = 'Yes'][1]").click()
                    else:
                        page.locator("// label[text() = 'Should every person eligible for the element automatically receive it?'] // following::label[text() = 'No'][1]").click()

                page.wait_for_timeout(2000)
                page.get_by_role("combobox", name="What is the earliest entry").click()
                page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_ERLST_ENTRY_DATE"]).click()
                page.get_by_role("combobox", name="What is the latest entry date").click()
                page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_LTST_ENTRY_DATE"]).click()

                # Standard Rules

                ###At which employment level should this element be attached?
                if datadictvalue["C_EMPLYMNT_LEVEL_ELMNT"] != 'N/A':
                    if datadictvalue["C_EMPLYMNT_LEVEL_ELMNT"]=='Assignment Level':
                        page.get_by_text("Assignment Level", exact=True).click()
                    elif datadictvalue["C_EMPLYMNT_LEVEL_ELMNT"]=='Term Level':
                        page.get_by_text("Term Level", exact=True).click()

                ### Does this element recur each payroll period, or does it require explicit entry?
                if datadictvalue["C_ELMNT_RCRRNG_NNRCRRNG"] != 'N/A':
                    if datadictvalue["C_ELMNT_RCRRNG_NNRCRRNG"]=='Recurring':
                        page.get_by_text("Recurring", exact=True).click()
                    elif datadictvalue["C_ELMNT_RCRRNG_NNRCRRNG"]=='Nonrecurring':
                        page.get_by_text("Nonrecurring", exact=True).click()

                ### Process the element only once in each payroll period?
                if datadictvalue["C_PRCSS_ELMNT_ONLY_ONCE"]!='N/A':
                    if datadictvalue["C_PRCSS_ELMNT_ONLY_ONCE"] == 'Yes':
                        page.locator("//label[text()='Process the element only once in each payroll period?']//following::label[text()='Yes'][1]").click()
                    elif datadictvalue["C_PRCSS_ELMNT_ONLY_ONCE"] == 'No':
                        page.locator("//label[text()='Process the element only once in each payroll period?']//following::label[text()='No'][1]").click()

                ### Can a person have more than one entry of this element in a payroll period?
                if datadictvalue["C_MORE_THAN_ONE_ENTRY"] != 'N/A':
                    if datadictvalue["C_MORE_THAN_ONE_ENTRY"] == 'Yes':
                        page.locator("//label[text()='Can a person have more than one entry of this element in a payroll period?']//following::label[text()='Yes'][1]").click()
                    elif datadictvalue["C_MORE_THAN_ONE_ENTRY"] == 'No':
                        page.locator("//label[text()='Can a person have more than one entry of this element in a payroll period?']//following::label[text()='No'][1]").click()

                ### Process and pay element separately or with other earnings elements?
                if datadictvalue["C_PRCSS_PAY"]=='Process and pay with other earnings':
                    page.locator("label").filter(has_text="Process and pay with other").click()
                elif datadictvalue["C_PRCSS_PAY"]=='Process separately, but pay with other earnings':
                    page.locator("label").filter(has_text="Process separately, but pay with other earnings").click()
                elif datadictvalue["C_PRCSS_PAY"] == 'Process separately and pay separately':
                    page.locator("label").filter(has_text="Process separately and pay separately").click()

                ### Tax this earning across multiple pay periods?
                if datadictvalue["C_TAX_MLTPL_PRODS"] != 'N/A':
                    if datadictvalue["C_TAX_MLTPL_PRODS"] == 'Yes':
                        page.locator("//label[text()='Tax this earning across multiple pay periods?']//following::label[text()='Yes'][1]").click()
                    elif datadictvalue["C_TAX_MLTPL_PRODS"] == 'No':
                        page.locator("//label[text()='Tax this earning across multiple pay periods?']//following::label[text()='No'][1]").click()

                ## Clicking on Next button
                page.get_by_role("button", name="Next").click()
                page.wait_for_timeout(3000)

                #Calculation Rules

                ### Selecting Conversion Rule as Flat amount
                if datadictvalue["C_CLCLTN_RULE"] == 'Flat amount':
                    page.get_by_text("Flat amount").first.click()

                    ### *What is the default periodicity of this element?
                    if datadictvalue["C_DFLT_PRDCTY"] !='N/A':
                        page.get_by_role("combobox", name="What is the default").click()
                        page.get_by_text(datadictvalue["C_DFLT_PRDCTY"]).click()
                    ### *Periodicity Conversion Rule
                    if datadictvalue["C_PRDCTY_CNVRSN_RULES"] != 'N/A':
                        page.get_by_role("combobox", name="Periodicity Conversion Rule").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRDCTY_CNVRSN_RULES"]).click()
                    ### How do you want the work units to be reported?
                    if datadictvalue["C_WORK_UNITS_RPRTD"] != 'N/A':
                        if datadictvalue["C_WORK_UNITS_RPRTD"] == 'Hours':
                            page.get_by_text("Hours", exact=True).click()
                        elif datadictvalue ["C_WORK_UNITS_RPRTD"] == 'None':
                            page.get_by_text("None", exact=True).click()
                    ### Work Units Conversion Rule
                    if datadictvalue["C_WORK_UNITS_CNVRSN_RULE"]!='N/A':
                        page.wait_for_timeout(3000)
                        page.get_by_role("combobox", name="Work Units Conversion Rule").click()
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_WORK_UNITS_CNVRSN_RULE"]).click()

                    # Special Rules
                    if datadictvalue["C_ELMNT_PRRTN"] == 'Yes':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='Yes'][1]").click()
                        page.wait_for_timeout(3000)
                        page.get_by_role("combobox", name="Proration Group").click()
                        page.get_by_text(datadictvalue["C_PRRTN_GROUP"]).click()
                        page.get_by_role("combobox", name="Proration Units").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_UNITS"]).click()
                        page.get_by_role("combobox", name="Proration Rate Conversion Rule").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_RATE_CNVRSN_RULE"]).click()
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"]=='Yes':
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                            page.wait_for_timeout(2000)
                            page.get_by_role("combobox", name="Retro Group").click()
                            page.wait_for_timeout(2000)
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                        else:
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()

                    elif datadictvalue["C_ELMNT_PRRTN"] == 'No':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='No'][1]").click()
                        page.wait_for_timeout(5000)
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                            page.wait_for_timeout(2000)
                            page.get_by_role("combobox", name="Retro Group").click()
                            page.wait_for_timeout(2000)
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                        else:
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                    elif datadictvalue["C_ELMNT_PRRTN"] == 'N/A':
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] != 'N/A':
                            if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                                page.wait_for_timeout(2000)
                                page.get_by_role("combobox", name="Retro Group").click()
                                page.wait_for_timeout(2000)
                                page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                            elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'No':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()

                    ### Use this element to calculate a gross amount from a specified net amount?
                    if datadictvalue["C_GROSS_AMNT_NET_AMNT"] != 'N/A':
                        if datadictvalue["C_GROSS_AMNT_NET_AMNT"] == 'Yes':
                            page.locator("//label[text()='Use this element to calculate a gross amount from a specified net amount?']//following::label[text()='Yes'][1]").click()
                        elif datadictvalue["C_GROSS_AMNT_NET_AMNT"] == 'No':
                            page.locator("//label[text()='Use this element to calculate a gross amount from a specified net amount?']//following::label[text()='No'][1]").click()

                ### Selecting Conversion Rule as Hours * Rate
                if datadictvalue["C_CLCLTN_RULE"] == 'Hours * Rate':
                    page.get_by_text("Hours * Rate").first.click()
                    page.wait_for_timeout(2000)
                    ### *What is the default periodicity of this element?
                    if datadictvalue["C_DFLT_PRDCTY"] != 'N/A':
                        page.get_by_role("combobox", name="What is the default").click()
                        page.get_by_text(datadictvalue["C_DFLT_PRDCTY"]).click()
                    ### *Periodicity Conversion Rule
                    if datadictvalue["C_PRDCTY_CNVRSN_RULES"] != 'N/A':
                        page.get_by_role("combobox", name="Periodicity Conversion Rule").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(
                            datadictvalue["C_PRDCTY_CNVRSN_RULES"]).click()
                    ### How do you want the work units to be reported?
                    if datadictvalue["C_WORK_UNITS_RPRTD"] != 'N/A':
                        if datadictvalue["C_WORK_UNITS_RPRTD"] == 'Hours':
                            page.get_by_text("Hours", exact=True).click()
                        elif datadictvalue["C_WORK_UNITS_RPRTD"] == 'None':
                            page.get_by_text("None", exact=True).click()
                    ### Work Units Conversion Rule
                    if datadictvalue["C_WORK_UNITS_CNVRSN_RULE"] != 'N/A':
                        page.wait_for_timeout(3000)
                        page.get_by_role("combobox", name="Work Units Conversion Rule").click()
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_WORK_UNITS_CNVRSN_RULE"]).click()

                    # Special Rules
                    if datadictvalue["C_ELMNT_PRRTN"] == 'Yes':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='Yes'][1]").click()
                        page.wait_for_timeout(3000)
                        page.get_by_role("combobox", name="Proration Group").click()
                        page.get_by_text(datadictvalue["C_PRRTN_GROUP"]).click()
                        page.get_by_role("combobox", name="Proration Units").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_UNITS"]).click()
                        page.get_by_role("combobox", name="Proration Rate Conversion Rule").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_RATE_CNVRSN_RULE"]).click()
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                            page.wait_for_timeout(2000)
                            page.get_by_role("combobox", name="Retro Group").click()
                            page.wait_for_timeout(2000)
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                        else:
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()

                    elif datadictvalue["C_ELMNT_PRRTN"] == 'No':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='No'][1]").click()
                        page.wait_for_timeout(5000)
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                            page.wait_for_timeout(2000)
                            page.get_by_role("combobox", name="Retro Group").click()
                            page.wait_for_timeout(2000)
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                        else:
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                    elif datadictvalue["C_ELMNT_PRRTN"] == 'N/A':
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] != 'N/A':
                            if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                                page.wait_for_timeout(2000)
                                page.get_by_role("combobox", name="Retro Group").click()
                                page.wait_for_timeout(2000)
                                page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                            elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'No':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()

                    ### Use this element to calculate a gross amount from a specified net amount?
                    if datadictvalue["C_GROSS_AMNT_NET_AMNT"] != 'N/A':
                        if datadictvalue["C_GROSS_AMNT_NET_AMNT"] == 'Yes':
                            page.locator("//label[text()='Use this element to calculate a gross amount from a specified net amount?']//following::label[text()='Yes'][1]").click()
                        elif datadictvalue["C_GROSS_AMNT_NET_AMNT"] == 'No':
                            page.locator("//label[text()='Use this element to calculate a gross amount from a specified net amount?']//following::label[text()='No'][1]").click()

                ### Selecting Conversion Rules as Factor
                if datadictvalue["C_CLCLTN_RULE"] == 'Factor':
                    page.get_by_text("Factor").first.click()
                    page.wait_for_timeout(2000)
                    ### *What is the default periodicity of this element?
                    if datadictvalue["C_DFLT_PRDCTY"] != 'N/A':
                        page.get_by_role("combobox", name="What is the default").click()
                        page.get_by_text(datadictvalue["C_DFLT_PRDCTY"]).click()
                    ### *Periodicity Conversion Rule
                    if datadictvalue["C_PRDCTY_CNVRSN_RULES"] != 'N/A':
                        page.get_by_role("combobox", name="Periodicity Conversion Rule").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRDCTY_CNVRSN_RULES"]).click()
                    ### How do you want the work units to be reported?
                    if datadictvalue["C_WORK_UNITS_RPRTD"] != 'N/A':
                        if datadictvalue["C_WORK_UNITS_RPRTD"] == 'Hours':
                            page.get_by_text("Hours", exact=True).click()
                        elif datadictvalue["C_WORK_UNITS_RPRTD"] == 'None':
                            page.get_by_text("None", exact=True).click()
                    ### Work Units Conversion Rule
                    if datadictvalue["C_WORK_UNITS_CNVRSN_RULE"] != 'N/A':
                        page.wait_for_timeout(3000)
                        page.get_by_role("combobox", name="Work Units Conversion Rule").click()
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_WORK_UNITS_CNVRSN_RULE"]).click()

                    # Special Rules
                    if datadictvalue["C_ELMNT_PRRTN"] == 'Yes':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='Yes'][1]").click()
                        page.wait_for_timeout(3000)
                        page.get_by_role("combobox", name="Proration Group").click()
                        page.get_by_text(datadictvalue["C_PRRTN_GROUP"]).click()
                        page.get_by_role("combobox", name="Proration Units").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_UNITS"]).click()
                        page.get_by_role("combobox", name="Proration Rate Conversion Rule").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_RATE_CNVRSN_RULE"]).click()
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                            page.wait_for_timeout(2000)
                            page.get_by_role("combobox", name="Retro Group").click()
                            page.wait_for_timeout(2000)
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                        else:
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()

                    elif datadictvalue["C_ELMNT_PRRTN"] == 'No':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='No'][1]").click()
                        page.wait_for_timeout(5000)
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                            page.wait_for_timeout(2000)
                            page.get_by_role("combobox", name="Retro Group").click()
                            page.wait_for_timeout(2000)
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                        else:
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                    elif datadictvalue["C_ELMNT_PRRTN"] == 'N/A':
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] != 'N/A':
                            if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                                page.wait_for_timeout(2000)
                                page.get_by_role("combobox", name="Retro Group").click()
                                page.wait_for_timeout(2000)
                                page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                            elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'No':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()

                    ### Use this element to calculate a gross amount from a specified net amount?
                    if datadictvalue["C_GROSS_AMNT_NET_AMNT"] != 'N/A':
                        if datadictvalue["C_GROSS_AMNT_NET_AMNT"] == 'Yes':
                            page.locator("//label[text()='Use this element to calculate a gross amount from a specified net amount?']//following::label[text()='Yes'][1]").click()
                        elif datadictvalue["C_GROSS_AMNT_NET_AMNT"] == 'No':
                            page.locator("//label[text()='Use this element to calculate a gross amount from a specified net amount?']//following::label[text()='No'][1]").click()

                ### Selecting Conversion Rules as Percentage of earnings
                if datadictvalue["C_CLCLTN_RULE"]=='Percentage of earnings':
                    page.get_by_text("Percentage of earning").first.click()
                    page.wait_for_timeout(2000)
                    ### *What is the default periodicity of this element?
                    if datadictvalue["C_DFLT_PRDCTY"] != 'N/A':
                        page.get_by_role("combobox", name="What is the default").click()
                        page.get_by_text(datadictvalue["C_DFLT_PRDCTY"]).click()
                    ### *Periodicity Conversion Rule
                    if datadictvalue["C_PRDCTY_CNVRSN_RULES"] != 'N/A':
                        page.get_by_role("combobox", name="Periodicity Conversion Rule").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRDCTY_CNVRSN_RULES"]).click()
                    ### How do you want the work units to be reported?
                    if datadictvalue["C_WORK_UNITS_RPRTD"] != 'N/A':
                        if datadictvalue["C_WORK_UNITS_RPRTD"] == 'Hours':
                            page.get_by_text("Hours", exact=True).click()
                        elif datadictvalue["C_WORK_UNITS_RPRTD"] == 'None':
                            page.get_by_text("None", exact=True).click()
                    ### Work Units Conversion Rule
                    if datadictvalue["C_WORK_UNITS_CNVRSN_RULE"] != 'N/A':
                        page.wait_for_timeout(3000)
                        page.get_by_role("combobox", name="Work Units Conversion Rule").click()
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_WORK_UNITS_CNVRSN_RULE"]).click()

                    # Special Rules
                    if datadictvalue["C_ELMNT_PRRTN"] == 'Yes':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='Yes'][1]").click()
                        page.wait_for_timeout(3000)
                        page.get_by_role("combobox", name="Proration Group").click()
                        page.get_by_text(datadictvalue["C_PRRTN_GROUP"]).click()
                        page.get_by_role("combobox", name="Proration Units").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_UNITS"]).click()
                        page.get_by_role("combobox", name="Proration Rate Conversion Rule").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_RATE_CNVRSN_RULE"]).click()
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                            page.wait_for_timeout(2000)
                            page.get_by_role("combobox", name="Retro Group").click()
                            page.wait_for_timeout(2000)
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                        else:
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()

                    elif datadictvalue["C_ELMNT_PRRTN"] == 'No':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='No'][1]").click()
                        page.wait_for_timeout(5000)
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                            page.wait_for_timeout(2000)
                            page.get_by_role("combobox", name="Retro Group").click()
                            page.wait_for_timeout(2000)
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                        else:
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_ELMNT_PRRTN"] == 'N/A':
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] != 'N/A':
                            if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                                page.wait_for_timeout(2000)
                                page.get_by_role("combobox", name="Retro Group").click()
                                page.wait_for_timeout(2000)
                                page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                            elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'No':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()

                    ### Use this element to calculate a gross amount from a specified net amount?
                    if datadictvalue["C_GROSS_AMNT_NET_AMNT"] != 'N/A':
                        if datadictvalue["C_GROSS_AMNT_NET_AMNT"] == 'Yes':
                            page.locator("//label[text()='Use this element to calculate a gross amount from a specified net amount?']//following::label[text()='Yes'][1]").click()
                        elif datadictvalue["C_GROSS_AMNT_NET_AMNT"] == 'No':
                            page.locator("//label[text()='Use this element to calculate a gross amount from a specified net amount?']//following::label[text()='No'][1]").click()

            # Overtime Rules
            if datadictvalue["C_ELMNT_ERNNGS_FLSA"] == 'Yes':
                page.locator("//label[text()='Should this element be included in the hours calculation of the overtime base rate?']//preceding::label[text()='Yes'][1]").click()
            else:
                page.locator("//label[text()='Should this element be included in the hours calculation of the overtime base rate?']//preceding::label[text()='No'][1]").click()

            if datadictvalue["C_ELMNT_HOURS_FLSA"] == 'Yes':
                page.locator("//label[text()='Should this element be included in the hours calculation of the overtime base rate?']//following::label[text()='Yes'][1]").click()
            else:
                page.locator("//label[text()='Should this element be included in the hours calculation of the overtime base rate?']//following::label[text()='No'][1]").click()
        # Secondary Classification as Educational Assistance
        if datadictvalue["C_SCNDRY_CLSSFCTN"]=='Educational Assistance':
            page.get_by_role("combobox", name="Secondary Classification").click()
            page.wait_for_timeout(3000)
            page.get_by_text(datadictvalue["C_SCNDRY_CLSSFCTN"], exact=True).click()
            page.wait_for_timeout(2000)
            if datadictvalue["C_CTGRY"]=='Standard':
                page.get_by_role("combobox", name="Category").click()
                page.wait_for_timeout(3000)
                page.get_by_text(datadictvalue["C_CTGRY"], exact=True).click()
                page.get_by_role("button", name="Continue").click()
                page.wait_for_timeout(3000)

                # Entering Basic Details
                page.get_by_label("Name", exact=True).type(datadictvalue["C_ELMNT_NAME"])
                page.get_by_label("Reporting Name").type(datadictvalue["C_RPRTNG_NAME"])
                page.get_by_label("Description").type(datadictvalue["C_DSCRPTN"])
                page.locator("//label[text()='Effective Date']//following::input[1]").clear()
                page.locator("//label[text()='Effective Date']//following::input[1]").type(datadictvalue["C_EFCTV_DATE"])

                # Selecting Currency
                page.get_by_role("combobox", name="Input Currency").click()
                page.wait_for_timeout(2000)
                page.get_by_text(datadictvalue["C_INPUT_CRNCY"],exact=True).click()

                # Selecting Duration
                ### Should every person eligible for the element automatically receive it?
                if datadictvalue["C_ATMTC_ELMNT_ELGBLTY"] != 'N/A':
                    if datadictvalue["C_ATMTC_ELMNT_ELGBLTY"] == 'Yes':
                        page.locator("// label[text() = 'Should every person eligible for the element automatically receive it?'] // following::label[text() = 'Yes'][1]").click()
                    else:
                        page.locator("// label[text() = 'Should every person eligible for the element automatically receive it?'] // following::label[text() = 'No'][1]").click()

                page.wait_for_timeout(2000)
                page.get_by_role("combobox", name="What is the earliest entry").click()
                page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_ERLST_ENTRY_DATE"]).click()
                page.get_by_role("combobox", name="What is the latest entry date").click()
                page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_LTST_ENTRY_DATE"]).click()

                # Standard Rules

                ###At which employment level should this element be attached?
                if datadictvalue["C_EMPLYMNT_LEVEL_ELMNT"] != 'N/A':
                    if datadictvalue["C_EMPLYMNT_LEVEL_ELMNT"]=='Assignment Level':
                        page.get_by_text("Assignment Level", exact=True).click()
                    elif datadictvalue["C_EMPLYMNT_LEVEL_ELMNT"]=='Term Level':
                        page.get_by_text("Term Level", exact=True).click()

                ### Does this element recur each payroll period, or does it require explicit entry?
                if datadictvalue["C_ELMNT_RCRRNG_NNRCRRNG"] != 'N/A':
                    if datadictvalue["C_ELMNT_RCRRNG_NNRCRRNG"]=='Recurring':
                        page.get_by_text("Recurring", exact=True).click()
                    elif datadictvalue["C_ELMNT_RCRRNG_NNRCRRNG"]=='Nonrecurring':
                        page.get_by_text("Nonrecurring", exact=True).click()

                ### Process the element only once in each payroll period?
                if datadictvalue["C_PRCSS_ELMNT_ONLY_ONCE"]!='N/A':
                    if datadictvalue["C_PRCSS_ELMNT_ONLY_ONCE"] == 'Yes':
                        page.locator("//label[text()='Process the element only once in each payroll period?']//following::label[text()='Yes'][1]").click()
                    elif datadictvalue["C_PRCSS_ELMNT_ONLY_ONCE"] == 'No':
                        page.locator("//label[text()='Process the element only once in each payroll period?']//following::label[text()='No'][1]").click()

                ### Can a person have more than one entry of this element in a payroll period?
                if datadictvalue["C_MORE_THAN_ONE_ENTRY"] != 'N/A':
                    if datadictvalue["C_MORE_THAN_ONE_ENTRY"] == 'Yes':
                        page.locator("//label[text()='Can a person have more than one entry of this element in a payroll period?']//following::label[text()='Yes'][1]").click()
                    elif datadictvalue["C_MORE_THAN_ONE_ENTRY"] == 'No':
                        page.locator("//label[text()='Can a person have more than one entry of this element in a payroll period?']//following::label[text()='No'][1]").click()

                ### Process and pay element separately or with other earnings elements?
                if datadictvalue["C_PRCSS_PAY"]=='Process and pay with other earnings':
                    page.locator("label").filter(has_text="Process and pay with other").click()
                elif datadictvalue["C_PRCSS_PAY"]=='Process separately, but pay with other earnings':
                    page.locator("label").filter(has_text="Process separately, but pay with other earnings").click()
                elif datadictvalue["C_PRCSS_PAY"] == 'Process separately and pay separately':
                    page.locator("label").filter(has_text="Process separately and pay separately").click()
                page.wait_for_timeout(2000)

                ### Tax this earning across multiple pay periods?
                if datadictvalue["C_TAX_MLTPL_PRODS"] != 'N/A':
                    if datadictvalue["C_TAX_MLTPL_PRODS"] == 'Yes':
                        page.locator("//label[text()='Tax this earning across multiple pay periods?']//following::label[text()='Yes'][1]").click()
                    elif datadictvalue["C_TAX_MLTPL_PRODS"] == 'No':
                        page.locator("//label[text()='Tax this earning across multiple pay periods?']//following::label[text()='No'][1]").click()

                ## Clicking on Next button
                page.get_by_role("button", name="Next").click()
                page.wait_for_timeout(3000)

                #Calculation Rules

                ### Selecting Conversion Rule as Flat amount
                if datadictvalue["C_CLCLTN_RULE"] == 'Flat amount':
                    page.get_by_text("Flat amount").first.click()

                    ### *What is the default periodicity of this element?
                    if datadictvalue["C_DFLT_PRDCTY"] !='N/A':
                        page.get_by_role("combobox", name="What is the default").click()
                        page.get_by_text(datadictvalue["C_DFLT_PRDCTY"]).click()
                    ### *Periodicity Conversion Rule
                    if datadictvalue["C_PRDCTY_CNVRSN_RULES"] != 'N/A':
                        page.get_by_role("combobox", name="Periodicity Conversion Rule").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRDCTY_CNVRSN_RULES"]).click()
                    ### How do you want the work units to be reported?
                    if datadictvalue["C_WORK_UNITS_RPRTD"] != 'N/A':
                        if datadictvalue["C_WORK_UNITS_RPRTD"] == 'Hours':
                            page.get_by_text("Hours", exact=True).click()
                        elif datadictvalue ["C_WORK_UNITS_RPRTD"] == 'None':
                            page.get_by_text("None", exact=True).click()
                    ### Work Units Conversion Rule
                    if datadictvalue["C_WORK_UNITS_CNVRSN_RULE"]!='N/A':
                        page.wait_for_timeout(3000)
                        page.get_by_role("combobox", name="Work Units Conversion Rule").click()
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_WORK_UNITS_CNVRSN_RULE"]).click()

                    # Special Rules
                    if datadictvalue["C_ELMNT_PRRTN"] == 'Yes':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='Yes'][1]").click()
                        page.wait_for_timeout(3000)
                        page.get_by_role("combobox", name="Proration Group").click()
                        page.get_by_text(datadictvalue["C_PRRTN_GROUP"]).click()
                        page.get_by_role("combobox", name="Proration Units").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_UNITS"]).click()
                        page.get_by_role("combobox", name="Proration Rate Conversion Rule").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_RATE_CNVRSN_RULE"]).click()
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"]=='Yes':
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                            page.wait_for_timeout(2000)
                            page.get_by_role("combobox", name="Retro Group").click()
                            page.wait_for_timeout(2000)
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                        else:
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()

                    elif datadictvalue["C_ELMNT_PRRTN"] == 'No':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='No'][1]").click()
                        page.wait_for_timeout(5000)
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] != 'N/A':
                            if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                                page.wait_for_timeout(2000)
                                page.get_by_role("combobox", name="Retro Group").click()
                                page.wait_for_timeout(2000)
                                page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                            elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'No':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_ELMNT_PRRTN"] == 'N/A':
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] != 'N/A':
                            if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                                page.wait_for_timeout(2000)
                                page.get_by_role("combobox", name="Retro Group").click()
                                page.wait_for_timeout(2000)
                                page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                            elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'No':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()

                    ### Use this element to calculate a gross amount from a specified net amount?
                    if datadictvalue["C_GROSS_AMNT_NET_AMNT"] != 'N/A':
                        if datadictvalue["C_GROSS_AMNT_NET_AMNT"] == 'Yes':
                            page.locator("//label[text()='Use this element to calculate a gross amount from a specified net amount?']//following::label[text()='Yes'][1]").click()
                        elif datadictvalue["C_GROSS_AMNT_NET_AMNT"] == 'No':
                            page.locator("//label[text()='Use this element to calculate a gross amount from a specified net amount?']//following::label[text()='No'][1]").click()

                ### Selecting Conversion Rule as Hours * Rate
                if datadictvalue["C_CLCLTN_RULE"] == 'Hours * Rate':
                    page.get_by_text("Hours * Rate").first.click()
                    page.wait_for_timeout(2000)
                    ### *What is the default periodicity of this element?
                    if datadictvalue["C_DFLT_PRDCTY"] != 'N/A':
                        page.get_by_role("combobox", name="What is the default").click()
                        page.get_by_text(datadictvalue["C_DFLT_PRDCTY"]).click()
                    ### *Periodicity Conversion Rule
                    if datadictvalue["C_PRDCTY_CNVRSN_RULES"] != 'N/A':
                        page.get_by_role("combobox", name="Periodicity Conversion Rule").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(
                            datadictvalue["C_PRDCTY_CNVRSN_RULES"]).click()
                    ### How do you want the work units to be reported?
                    if datadictvalue["C_WORK_UNITS_RPRTD"] != 'N/A':
                        if datadictvalue["C_WORK_UNITS_RPRTD"] == 'Hours':
                            page.get_by_text("Hours", exact=True).click()
                        elif datadictvalue["C_WORK_UNITS_RPRTD"] == 'None':
                            page.get_by_text("None", exact=True).click()
                    ### Work Units Conversion Rule
                    if datadictvalue["C_WORK_UNITS_CNVRSN_RULE"] != 'N/A':
                        page.wait_for_timeout(3000)
                        page.get_by_role("combobox", name="Work Units Conversion Rule").click()
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_WORK_UNITS_CNVRSN_RULE"]).click()

                    # Special Rules
                    if datadictvalue["C_ELMNT_PRRTN"] == 'Yes':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='Yes'][1]").click()
                        page.wait_for_timeout(3000)
                        page.get_by_role("combobox", name="Proration Group").click()
                        page.get_by_text(datadictvalue["C_PRRTN_GROUP"]).click()
                        page.get_by_role("combobox", name="Proration Units").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_UNITS"]).click()
                        page.get_by_role("combobox", name="Proration Rate Conversion Rule").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_RATE_CNVRSN_RULE"]).click()
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                            page.wait_for_timeout(2000)
                            page.get_by_role("combobox", name="Retro Group").click()
                            page.wait_for_timeout(2000)
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                        else:
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()

                    elif datadictvalue["C_ELMNT_PRRTN"] == 'No':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='No'][1]").click()
                        page.wait_for_timeout(5000)
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] != 'N/A':
                            if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                                page.wait_for_timeout(2000)
                                page.get_by_role("combobox", name="Retro Group").click()
                                page.wait_for_timeout(2000)
                                page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                            elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'No':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_ELMNT_PRRTN"] == 'N/A':
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] != 'N/A':
                            if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                                page.wait_for_timeout(2000)
                                page.get_by_role("combobox", name="Retro Group").click()
                                page.wait_for_timeout(2000)
                                page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                            elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'No':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()

                    ### Use this element to calculate a gross amount from a specified net amount?
                    if datadictvalue["C_GROSS_AMNT_NET_AMNT"] != 'N/A':
                        if datadictvalue["C_GROSS_AMNT_NET_AMNT"] == 'Yes':
                            page.locator("//label[text()='Use this element to calculate a gross amount from a specified net amount?']//following::label[text()='Yes'][1]").click()
                        elif datadictvalue["C_GROSS_AMNT_NET_AMNT"] == 'No':
                            page.locator("//label[text()='Use this element to calculate a gross amount from a specified net amount?']//following::label[text()='No'][1]").click()

                ### Selecting Conversion Rules as Factor
                if datadictvalue["C_CLCLTN_RULE"] == 'Factor':
                    page.get_by_text("Factor").first.click()
                    page.wait_for_timeout(2000)
                    ### *What is the default periodicity of this element?
                    if datadictvalue["C_DFLT_PRDCTY"] != 'N/A':
                        page.get_by_role("combobox", name="What is the default").click()
                        page.get_by_text(datadictvalue["C_DFLT_PRDCTY"]).click()
                    ### *Periodicity Conversion Rule
                    if datadictvalue["C_PRDCTY_CNVRSN_RULES"] != 'N/A':
                        page.get_by_role("combobox", name="Periodicity Conversion Rule").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRDCTY_CNVRSN_RULES"]).click()
                    ### How do you want the work units to be reported?
                    if datadictvalue["C_WORK_UNITS_RPRTD"] != 'N/A':
                        if datadictvalue["C_WORK_UNITS_RPRTD"] == 'Hours':
                            page.get_by_text("Hours", exact=True).click()
                        elif datadictvalue["C_WORK_UNITS_RPRTD"] == 'None':
                            page.get_by_text("None", exact=True).click()
                    ### Work Units Conversion Rule
                    if datadictvalue["C_WORK_UNITS_CNVRSN_RULE"] != 'N/A':
                        page.wait_for_timeout(3000)
                        page.get_by_role("combobox", name="Work Units Conversion Rule").click()
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_WORK_UNITS_CNVRSN_RULE"]).click()

                    # Special Rules
                    if datadictvalue["C_ELMNT_PRRTN"] == 'Yes':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='Yes'][1]").click()
                        page.wait_for_timeout(3000)
                        page.get_by_role("combobox", name="Proration Group").click()
                        page.get_by_text(datadictvalue["C_PRRTN_GROUP"]).click()
                        page.get_by_role("combobox", name="Proration Units").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_UNITS"]).click()
                        page.get_by_role("combobox", name="Proration Rate Conversion Rule").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_RATE_CNVRSN_RULE"]).click()
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                            page.wait_for_timeout(2000)
                            page.get_by_role("combobox", name="Retro Group").click()
                            page.wait_for_timeout(2000)
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                        else:
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()

                    elif datadictvalue["C_ELMNT_PRRTN"] == 'No':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='No'][1]").click()
                        page.wait_for_timeout(5000)
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] != 'N/A':
                            if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                                page.wait_for_timeout(2000)
                                page.get_by_role("combobox", name="Retro Group").click()
                                page.wait_for_timeout(2000)
                                page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                            elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'No':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_ELMNT_PRRTN"] == 'N/A':
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] != 'N/A':
                            if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                                page.wait_for_timeout(2000)
                                page.get_by_role("combobox", name="Retro Group").click()
                                page.wait_for_timeout(2000)
                                page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                            elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'No':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()

                    ### Use this element to calculate a gross amount from a specified net amount?
                    if datadictvalue["C_GROSS_AMNT_NET_AMNT"] != 'N/A':
                        if datadictvalue["C_GROSS_AMNT_NET_AMNT"] == 'Yes':
                            page.locator("//label[text()='Use this element to calculate a gross amount from a specified net amount?']//following::label[text()='Yes'][1]").click()
                        elif datadictvalue["C_GROSS_AMNT_NET_AMNT"] == 'No':
                            page.locator("//label[text()='Use this element to calculate a gross amount from a specified net amount?']//following::label[text()='No'][1]").click()

                ### Selecting Conversion Rules as Percentage of earnings
                if datadictvalue["C_CLCLTN_RULE"]=='Percentage of earnings':
                    page.get_by_text("Percentage of earning").first.click()
                    page.wait_for_timeout(2000)
                    ### *What is the default periodicity of this element?
                    if datadictvalue["C_DFLT_PRDCTY"] != 'N/A':
                        page.get_by_role("combobox", name="What is the default").click()
                        page.get_by_text(datadictvalue["C_DFLT_PRDCTY"]).click()
                    ### *Periodicity Conversion Rule
                    if datadictvalue["C_PRDCTY_CNVRSN_RULES"] != 'N/A':
                        page.get_by_role("combobox", name="Periodicity Conversion Rule").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRDCTY_CNVRSN_RULES"]).click()
                    ### How do you want the work units to be reported?
                    if datadictvalue["C_WORK_UNITS_RPRTD"] != 'N/A':
                        if datadictvalue["C_WORK_UNITS_RPRTD"] == 'Hours':
                            page.get_by_text("Hours", exact=True).click()
                        elif datadictvalue["C_WORK_UNITS_RPRTD"] == 'None':
                            page.get_by_text("None", exact=True).click()
                    ### Work Units Conversion Rule
                    if datadictvalue["C_WORK_UNITS_CNVRSN_RULE"] != 'N/A':
                        page.wait_for_timeout(3000)
                        page.get_by_role("combobox", name="Work Units Conversion Rule").click()
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_WORK_UNITS_CNVRSN_RULE"]).click()

                    # Special Rules
                    if datadictvalue["C_ELMNT_PRRTN"] == 'Yes':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='Yes'][1]").click()
                        page.wait_for_timeout(3000)
                        page.get_by_role("combobox", name="Proration Group").click()
                        page.get_by_text(datadictvalue["C_PRRTN_GROUP"]).click()
                        page.get_by_role("combobox", name="Proration Units").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_UNITS"]).click()
                        page.get_by_role("combobox", name="Proration Rate Conversion Rule").click()
                        page.wait_for_timeout(2000)
                        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_RATE_CNVRSN_RULE"]).click()
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                            page.wait_for_timeout(2000)
                            page.get_by_role("combobox", name="Retro Group").click()
                            page.wait_for_timeout(2000)
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                        else:
                            page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()

                    elif datadictvalue["C_ELMNT_PRRTN"] == 'No':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='No'][1]").click()
                        page.wait_for_timeout(5000)
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] != 'N/A':
                            if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                                page.wait_for_timeout(2000)
                                page.get_by_role("combobox", name="Retro Group").click()
                                page.wait_for_timeout(2000)
                                page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                            elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'No':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_ELMNT_PRRTN"] == 'N/A':
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] != 'N/A':
                            if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                                page.wait_for_timeout(2000)
                                page.get_by_role("combobox", name="Retro Group").click()
                                page.wait_for_timeout(2000)
                                page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()
                            elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'No':
                                page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()

                    ### Use this element to calculate a gross amount from a specified net amount?
                    if datadictvalue["C_GROSS_AMNT_NET_AMNT"] != 'N/A':
                        if datadictvalue["C_GROSS_AMNT_NET_AMNT"] == 'Yes':
                            page.locator("//label[text()='Use this element to calculate a gross amount from a specified net amount?']//following::label[text()='Yes'][1]").click()
                        elif datadictvalue["C_GROSS_AMNT_NET_AMNT"] == 'No':
                            page.locator("//label[text()='Use this element to calculate a gross amount from a specified net amount?']//following::label[text()='No'][1]").click()

            # Overtime Rules
            if datadictvalue["C_ELMNT_ERNNGS_FLSA"] == 'Yes':
                page.locator("//label[text()='Should this element be included in the hours calculation of the overtime base rate?']//preceding::label[text()='Yes'][1]").click()
            else:
                page.locator("//label[text()='Should this element be included in the hours calculation of the overtime base rate?']//preceding::label[text()='No'][1]").click()

            if datadictvalue["C_ELMNT_HOURS_FLSA"] == 'Yes':
                page.locator("//label[text()='Should this element be included in the hours calculation of the overtime base rate?']//following::label[text()='Yes'][1]").click()
            else:
                page.locator("//label[text()='Should this element be included in the hours calculation of the overtime base rate?']//following::label[text()='No'][1]").click()

        # Moving to Next Page
        page.get_by_role("button", name="Next").click()
        page.wait_for_timeout(3000)
        # Saving the Record
        page.get_by_role("button", name="Submit").click()
        page.wait_for_timeout(30000)
        page.locator("//span[text()='K']").click()
        page.wait_for_timeout(20000)
        if page.locator("//span[text()='K']").is_visible():
            page.locator("//span[text()='K']").click()
            page.wait_for_timeout(10000)
        try:
            expect(page.locator("//h1[text()='Elements']")).to_be_visible()
            page.wait_for_timeout(3000)
            print("Element Entry Created Successfully")
            datadictvalue["RowStatus"] = "Element Saved"
        except Exception as e:
            print("Unable to Create the Element Entry")
            datadictvalue["RowStatus"] = "Unable to Create the Element Entry"

        i = i + 1

    OraSignOut(page, context, browser, videodir)
    return datadict

# ****** Execution Starts Here ******
print("Process Started At - ", datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
if CheckWrkbkForProcessing(SOURCE_DIR_PATH + OTHER_DEDUCTIONS, NONPAYROLL_ELEMENTS):
    CreateWrkbkForProcessing(SOURCE_DIR_PATH + OTHER_DEDUCTIONS, NONPAYROLL_ELEMENTS,PRCS_DIR_PATH + OTHER_DEDUCTIONS)
    rows, cols, datadictwrkbk = ImportWrkbk(PRCS_DIR_PATH + OTHER_DEDUCTIONS, NONPAYROLL_ELEMENTS)
    if rows > 0:
        with sync_playwright() as pw:
            output = configure(pw, rows, datadictwrkbk,VIDEO_DIR_PATH + re.split(".xlsx", OTHER_DEDUCTIONS)[0] + "_" + NONPAYROLL_ELEMENTS)
        write_status(output, RESULTS_DIR_PATH + re.split(".xlsx", OTHER_DEDUCTIONS)[0]+ "_" + NONPAYROLL_ELEMENTS + "_Results_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".xlsx")
    else:
        print("No data rows to process. Check the source workbook to ensure it is valid!")
print("Process Ended At - ", datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

